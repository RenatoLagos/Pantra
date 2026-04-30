"""Conversation pipeline — the seam that wires inbound messages to LLM + tools.

`process_inbound` is channel-agnostic. It returns an `OutboundMessage`. The
caller decides how to deliver it (WhatsApp adapter, web HTTP response, …).
`handle_inbound_whatsapp` is the WhatsApp-specific orchestrator that the
webhook background task uses.
"""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pantra.audio import storage as audio_storage
from pantra.audio import synthesizer as audio_synthesizer
from pantra.audio import transcriber as audio_transcriber
from pantra.channels.whatsapp import media as whatsapp_media
from pantra.channels.whatsapp.adapter import WhatsAppAdapter
from pantra.channels.whatsapp.normalizer import InboundMessage
from pantra.channels.whatsapp.window import is_within_window
from pantra.config import settings
from pantra.db import session_scope
from pantra.handoff import dispatch as dispatch_handoff
from pantra.llm.classifier import Classifier, ClassifierOutput
from pantra.llm.engine import ConversationEngine, EngineResult
from pantra.llm.memory.window import WindowMessage, load_window
from pantra.llm.prompts.system import build_system_prompt
from pantra.llm.router import choose
from pantra.logging import log
from pantra.models import (
    AIRun,
    Business,
    Channel,
    ChannelType,
    Conversation,
    ConversationStatus,
    Customer,
    HandoffStatus,
    HandoffTask,
    Message,
    MessageSender,
    Practitioner,
    Service,
)
from pantra.privacy import pii
from pantra.tools import REGISTRY as TOOL_REGISTRY
from pantra.tools import ToolContext, anthropic_tool_definitions, get_tool

MAX_TOOL_TURNS = 5
DEMO_IDLE_RESET = timedelta(minutes=30)


@dataclass(slots=True)
class OutboundMessage:
    text: str | None = None
    audio_url: str | None = None
    handoff_triggered: bool = False
    skipped_reason: str | None = None


# ─── Public entry points ────────────────────────────────────────────────

async def handle_inbound_whatsapp(inbound: InboundMessage) -> None:
    """WhatsApp orchestrator. Persists, processes, sends via Meta Cloud API."""
    async with session_scope() as session:
        outcome = await process_inbound(session, inbound)

    if outcome.handoff_triggered or outcome.skipped_reason:
        return
    if not outcome.text and not outcome.audio_url:
        return

    adapter = WhatsAppAdapter(phone_number_id=inbound.channel_account_id)
    if outcome.audio_url:
        await adapter.send_audio(to=inbound.external_user_id, audio_url=outcome.audio_url)
    if outcome.text:
        await adapter.send_text(to=inbound.external_user_id, body=outcome.text)


# Backwards-compatible alias used by api/webhooks/whatsapp.py.
handle_inbound_message = handle_inbound_whatsapp


async def process_inbound(session: AsyncSession, inbound: InboundMessage) -> OutboundMessage:
    """Run the full pipeline against an open AsyncSession.

    Caller is responsible for committing the session (session_scope() does
    that automatically).
    """
    business, customer, conversation = await _resolve_entities(session, inbound)

    if customer.opted_out:
        return OutboundMessage(skipped_reason="customer_opted_out")

    if not await _persist_inbound_idempotent(session, conversation, inbound):
        return OutboundMessage(skipped_reason="duplicate_delivery")

    if conversation.status == ConversationStatus.human_needed:
        if not business.is_demo:
            return OutboundMessage(skipped_reason="conversation_in_handoff")
        # Demo: never freeze. Reset and keep going. The HandoffTask stays in
        # DB so analytics still see "this prospect would have been handed off".
        conversation.status = ConversationStatus.active
        log.info("conversation.demo_resume_after_handoff", conversation_id=str(conversation.id))

    # Resolve audio → text if needed. Pass the customer's *learned* language
    # only — letting Whisper auto-detect when we don't have one yet, instead
    # of biasing it toward the business default.
    whisper_lang = customer.preferred_language  # None on first contact
    if inbound.text is None and inbound.audio_media_id and inbound.channel == "whatsapp":
        audio_bytes = await whatsapp_media.download_media(inbound.audio_media_id)
        inbound.text = await audio_transcriber.transcribe(
            audio_bytes,
            language=whisper_lang,
            filename_hint="whatsapp.ogg",
        )
        await _attach_transcription(session, conversation, inbound)
    elif inbound.text is None and (inbound.raw or {}).get("audio_path") and inbound.channel == "web":
        inbound.text = await audio_transcriber.transcribe(
            (inbound.raw or {})["audio_path"],
            language=whisper_lang,
        )
        await _attach_transcription(session, conversation, inbound)

    if not inbound.text:
        return OutboundMessage(skipped_reason="no_text_after_transcription")

    # Classify
    classifier = Classifier()
    classification = await classifier.classify(
        text=inbound.text, business_domain=business.domain.value
    )
    await _persist_ai_run(
        session,
        conversation,
        role="classifier",
        classification=classification,
        prompt_text=pii.redact(inbound.text),
    )

    # Update language hints from classifier. conversation.language drives
    # the system prompt for the current chat; customer.preferred_language
    # is the cross-conversation memory that next time will skip the
    # Whisper/classifier "guess" step.
    if classification.language:
        if conversation.language != classification.language:
            conversation.language = classification.language
        if customer.preferred_language != classification.language:
            customer.preferred_language = classification.language

    # Handoff path
    if classification.needs_human:
        await _open_handoff(session, business, conversation, customer, inbound, classification)
        if not business.is_demo:
            return OutboundMessage(handoff_triggered=True)
        # Demo: handoff is recorded for analytics, but we keep replying so
        # the prospect can keep evaluating the bot.

    # LLM tool-use loop. The `messages` list grows across turns: each
    # assistant turn (with tool_use blocks) and each user turn (with
    # tool_result blocks) is appended in place. Anthropic requires every
    # tool_result block to have a matching tool_use in the prior message.
    history = await load_window(session, conversation_id=conversation.id)
    language = (
        conversation.language
        or customer.preferred_language
        or business.default_language
    )
    knowledge = await _load_knowledge(session, business, language=language)
    system_prompt = build_system_prompt(
        business=business,
        customer=customer,
        conversation=conversation,
        knowledge_snippets=knowledge,
    )
    engine = ConversationEngine()
    tool_defs = anthropic_tool_definitions(list(TOOL_REGISTRY.values()))

    messages: list[dict] = [
        {"role": m.role, "content": m.content}
        for m in history
        if m.role != "system"
    ]

    reply_text: str | None = None
    for _ in range(MAX_TOOL_TURNS):
        result = await engine.step(
            system_prompt=system_prompt,
            messages=messages,
            tool_definitions=tool_defs,
        )
        await _persist_ai_run(session, conversation, role="main", engine_result=result)

        if result.tool_calls:
            # Preserve the assistant turn so the next request has the
            # corresponding tool_use blocks for our tool_result blocks.
            messages.append({"role": "assistant", "content": result.assistant_blocks})

            tool_results = await _execute_tools(
                session, business, customer, conversation, inbound, result.tool_calls
            )
            messages.append({"role": "user", "content": tool_results})

            if any(tc.get("name") == "handoff_to_human" for tc in result.tool_calls):
                if not business.is_demo:
                    return OutboundMessage(handoff_triggered=True)
                # Demo: tool already logged + dispatched (or skipped). Keep
                # looping so the engine produces a final user-visible reply.
        else:
            reply_text = result.reply_text
            break

    if not reply_text:
        return OutboundMessage(skipped_reason="empty_engine_reply")

    # Persist the AI reply
    await _persist_ai_reply(session, conversation, reply_text)
    conversation.last_message_at = datetime.now(tz=timezone.utc)

    # WhatsApp 24h window check before sending free text
    if conversation.channel_type == ChannelType.whatsapp:
        if not is_within_window(conversation.last_inbound_at):
            log.warning("conversation.outside_window", conversation_id=str(conversation.id))
            return OutboundMessage(skipped_reason="outside_24h_window")

    # TTS if applicable
    audio_url: str | None = None
    if _should_use_tts(business, inbound):
        try:
            audio_bytes = await audio_synthesizer.synthesize(
                reply_text, voice_id=(business.config or {}).get("voice_id")
            )
            ref = await audio_storage.save_audio(audio_bytes, suffix="mp3")
            audio_url = ref.public_url
        except Exception as e:
            # TTS failures must NOT block the text reply.
            log.warning("conversation.tts_failed", error=str(e))

    return OutboundMessage(text=reply_text, audio_url=audio_url)


# ─── Helpers ────────────────────────────────────────────────────────────

async def _resolve_entities(
    session: AsyncSession, inbound: InboundMessage
) -> tuple[Business, Customer, Conversation]:
    if inbound.channel == "web":
        # The web demo uses the business slug as channel_account_id.
        biz_stmt = select(Business).where(Business.slug == inbound.channel_account_id)
        business = (await session.execute(biz_stmt)).scalar_one_or_none()
        if not business:
            raise ValueError(f"unknown demo business slug: {inbound.channel_account_id!r}")
        channel_type = ChannelType.web
    else:
        # WhatsApp: resolve Channel by external_account_id (phone_number_id).
        chan_stmt = select(Channel).where(
            Channel.type == ChannelType.whatsapp,
            Channel.external_account_id == inbound.channel_account_id,
        )
        channel = (await session.execute(chan_stmt)).scalar_one_or_none()
        if not channel:
            raise ValueError(
                f"no channel registered for phone_number_id={inbound.channel_account_id!r}"
            )
        business = await session.get(Business, channel.business_id)
        if not business:
            raise ValueError(f"business missing for channel {channel.id}")
        channel_type = ChannelType.whatsapp

    cust_stmt = select(Customer).where(
        Customer.business_id == business.id,
        Customer.channel_type == channel_type,
        Customer.external_user_id == inbound.external_user_id,
    )
    customer = (await session.execute(cust_stmt)).scalar_one_or_none()
    if not customer:
        # preferred_language is intentionally left null — it's a long-term
        # signal, not a guess. We only fill it once the classifier detects a
        # language with confidence.
        customer = Customer(
            business_id=business.id,
            channel_type=channel_type,
            external_user_id=inbound.external_user_id,
            name=inbound.user_display_name,
            preferred_language=None,
            is_demo=business.is_demo,
        )
        session.add(customer)
        await session.flush()

    conv_stmt = (
        select(Conversation)
        .where(
            Conversation.business_id == business.id,
            Conversation.customer_id == customer.id,
            Conversation.status.in_(
                [
                    ConversationStatus.active,
                    ConversationStatus.waiting_customer,
                    ConversationStatus.human_needed,
                ]
            ),
        )
        .order_by(Conversation.created_at.desc())
    )
    conversation = (await session.execute(conv_stmt)).scalar_one_or_none()

    # Demo idle reset: if the prospect's last activity was more than
    # DEMO_IDLE_RESET ago, treat their next message as a fresh chat.
    # Prevents stale context from bleeding across demo sessions.
    if business.is_demo and conversation:
        last_active = conversation.last_message_at or conversation.created_at
        if last_active and (datetime.now(tz=timezone.utc) - last_active) >= DEMO_IDLE_RESET:
            conversation.status = ConversationStatus.closed
            await session.flush()
            conversation = None

    if not conversation:
        conversation = Conversation(
            business_id=business.id,
            customer_id=customer.id,
            channel_type=channel_type,
            language=business.default_language,
            is_demo=business.is_demo,
        )
        session.add(conversation)
        await session.flush()

    return business, customer, conversation


async def _persist_inbound_idempotent(
    session: AsyncSession, conversation: Conversation, inbound: InboundMessage
) -> bool:
    if inbound.external_message_id:
        existing = await session.execute(
            select(Message.id).where(
                Message.conversation_id == conversation.id,
                Message.channel_message_id == inbound.external_message_id,
            )
        )
        if existing.first():
            return False

    msg = Message(
        conversation_id=conversation.id,
        sender=MessageSender.customer,
        channel_message_id=inbound.external_message_id,
        text=inbound.text,
        raw_payload=inbound.raw,
    )
    session.add(msg)
    conversation.last_inbound_at = inbound.received_at
    conversation.last_message_at = inbound.received_at
    await session.flush()
    return True


async def _attach_transcription(
    session: AsyncSession, conversation: Conversation, inbound: InboundMessage
) -> None:
    if not inbound.external_message_id:
        return
    msg = (
        await session.execute(
            select(Message).where(
                Message.conversation_id == conversation.id,
                Message.channel_message_id == inbound.external_message_id,
            )
        )
    ).scalar_one_or_none()
    if msg:
        msg.text = inbound.text
        await session.flush()


async def _persist_ai_run(
    session: AsyncSession,
    conversation: Conversation,
    *,
    role: str,
    classification: ClassifierOutput | None = None,
    engine_result: EngineResult | None = None,
    prompt_text: str | None = None,
) -> None:
    choice = choose(role)  # type: ignore[arg-type]
    run = AIRun(
        conversation_id=conversation.id,
        role=role,
        provider=choice.provider,
        model=choice.model,
        classifier_output=classification.model_dump() if classification else None,
        input_tokens=engine_result.input_tokens if engine_result else None,
        output_tokens=engine_result.output_tokens if engine_result else None,
        latency_ms=engine_result.latency_ms if engine_result else None,
        redacted_prompt=prompt_text,
    )
    session.add(run)
    await session.flush()


async def _open_handoff(
    session: AsyncSession,
    business: Business,
    conversation: Conversation,
    customer: Customer,
    inbound: InboundMessage,
    classification: ClassifierOutput,
) -> None:
    safe_text = pii.redact(inbound.text or "")
    summary = (
        f"Customer ({customer.name or customer.external_user_id}) — "
        f"intent={classification.intent}, urgency={classification.urgency}\n"
        f"Last message: {safe_text[:300]}"
    )
    task = HandoffTask(
        business_id=business.id,
        conversation_id=conversation.id,
        reason=f"classifier:{classification.intent or 'unknown'}",
        priority=1 if classification.urgency == "high" else 2,
        status=HandoffStatus.open,
        summary=summary,
    )
    session.add(task)
    # In prod, freeze the conversation so the human can take over.
    # In demo, leave the conversation active — the prospect should be able
    # to keep poking the bot.
    if not business.is_demo:
        conversation.status = ConversationStatus.human_needed
    await session.flush()

    await dispatch_handoff(
        task,
        business_id=business.id,
        conversation_id=conversation.id,
        is_demo=business.is_demo,
    )


async def _execute_tools(
    session: AsyncSession,
    business: Business,
    customer: Customer,
    conversation: Conversation,
    inbound: InboundMessage,
    tool_calls: list[dict],
) -> list[dict]:
    results: list[dict] = []
    for call in tool_calls:
        name = call.get("name", "")
        try:
            tool = get_tool(name)
            payload = tool.input_model.model_validate(call.get("input") or {})
            ctx = ToolContext(
                business_id=business.id,
                customer_id=customer.id,
                conversation_id=conversation.id,
                session=session,
                idempotency_key=f"{inbound.channel}:{inbound.external_message_id}:{call.get('id')}",
            )
            output = await tool.run(ctx, payload)
            results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": call.get("id"),
                    "content": output.model_dump_json(),
                }
            )
        except Exception as e:
            log.warning("tools.execution_failed", tool=name, error=str(e))
            results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": call.get("id"),
                    "content": json.dumps({"error": str(e)}),
                    "is_error": True,
                }
            )
    return results


async def _persist_ai_reply(
    session: AsyncSession, conversation: Conversation, text: str
) -> None:
    msg = Message(
        conversation_id=conversation.id,
        sender=MessageSender.ai,
        text=text,
    )
    session.add(msg)
    await session.flush()


async def _load_knowledge(
    session: AsyncSession,
    business: Business,
    *,
    language: str,
) -> list[str]:
    """Compose the knowledge snippets the system prompt embeds.

    Layered:
      1. Static `business.config.knowledge` bullets (always-relevant info).
      2. Cancellation policy in the patient's language (always relevant).
      3. Services catalog with IDs.
      4. Practitioner roster with IDs.

    Anything LARGE (FAQs, treatment long-form details) is intentionally NOT
    in the system prompt — the LLM calls `search_knowledge` /
    `get_treatment_details` when the patient asks about it.
    """
    config = business.config or {}
    snippets: list[str] = list(config.get("knowledge", []))

    policy = (config.get("cancellation_policy") or {}).get("human_text") or {}
    policy_text = policy.get(language) or policy.get(business.default_language) or policy.get("en")
    if policy_text:
        snippets.append(f"Cancellation policy: {policy_text}")

    services = (
        await session.execute(
            select(Service).where(
                Service.business_id == business.id,
                Service.is_active.is_(True),
            )
        )
    ).scalars().all()
    if services:
        snippets.append("Services catalog (use service_id when calling tools):")
        for s in services:
            price = f" — €{s.price_cents / 100:.0f}" if s.price_cents else ""
            snippets.append(
                f"  • [service_id={s.id}] {s.name} ({s.duration_minutes} min{price}) — code: {s.code}"
            )

    practitioners = (
        await session.execute(
            select(Practitioner).where(
                Practitioner.business_id == business.id,
                Practitioner.is_active.is_(True),
            )
        )
    ).scalars().all()
    if practitioners:
        snippets.append("Practitioners (use practitioner_id when the customer prefers one):")
        for p in practitioners:
            specs = ", ".join(p.specialties) if p.specialties else "general"
            langs = ", ".join(p.languages) if p.languages else "—"
            snippets.append(
                f"  • [practitioner_id={p.id}] {p.display_name} — {specs} (idiomas: {langs})"
            )

    return snippets


def _should_use_tts(business: Business, inbound: InboundMessage) -> bool:
    config = business.config or {}
    mode = config.get("tts_mode", settings.tts_default_mode)
    if mode == "text_only":
        return False
    if mode == "audio_always":
        return True
    # mirror: audio iff inbound was audio
    raw = inbound.raw or {}
    return bool(inbound.audio_media_id) or raw.get("kind") == "audio" or raw.get("type") == "audio"
