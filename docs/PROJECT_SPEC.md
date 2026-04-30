# Pantra — Product Spec (MVP)

Status: **active** — decisions closed 2026-04-27. Pivoted to dental-clinic
focus 2026-04-30. Living document.

## 1. What Pantra is

A multilingual AI conversational assistant **for dental clinics** in Berlin.
Receives WhatsApp messages, replies with a natural human-like tone, and
connects to appointment booking, no-show reminders, calendar, and human
handoff.

**One sentence**: the AI assistant that talks like someone from your team.

## 2. Business model (single Pro plan at launch)

- Monthly: **€450/mo**
- Optional setup: **€1,500–€3,000**
- Channel: **WhatsApp** (Instagram deferred to Phase 2)
- Languages MVP: **DE, EN, ES, TR** (Berlin demographics → Turkish in MVP)
- Included: AI assistant, multilingual chat, Google Calendar, booking /
  appointment / lead workflows, basic CRM, human handoff (Telegram/email),
  monthly report, business knowledge base.

## 3. Closed decisions (2026-04-27)

| # | Decision | Reason |
|---|----------|--------|
| 1 | Stack: **FastAPI + Python 3.12** | LLM ecosystem maturity, single-dev velocity. |
| 2 | Channel MVP: **WhatsApp only** | Meta verification + 24h window already a multi-week effort; clone adapter for IG in Phase 2. |
| 3 | Handoff: **Telegram bot + email** (NO admin dashboard at MVP) | Building a full inbox doubles eng work; Telegram + email is enough for first 3–5 clients and gives instant push to the owner's phone. |
| 4 | LLM stack: **1 classifier + 1 main** | Haiku 4.5 / Gemini Flash for classifier; Sonnet 4.6 for main. 4-tier router is premature optimization. |
| 5 | Booking concurrency: **idempotency keys + `SELECT FOR UPDATE` + verify-then-commit** | Two customers can hit the same slot at the same time. |
| 6 | WhatsApp 24h window: **parametrized template system + window detector + send-template fallback** | Outside the 24h window only approved templates can be sent. |
| 7 | Conversation memory: **sliding window of last N messages + rolling summary + structured customer memory** (separate from transcript) | LLM context is finite; long conversations need bounded prompts. |
| 8 | Eval pipeline: **case-based runner** (Promptfoo-compatible cases) on every prompt change | Manual test cases ≠ regression safety. |
| 9 | Privacy: **PII redaction in logs + 7-day retention for prompt logs + customer opt-out** | GDPR compliance + DE market. |
| 10 | No-show reduction: **T-24h + T-2h reminder + explicit confirm + auto re-booking on cancel** | This is a sellable clinic feature. |

### Spec contradictions resolved

- **Turkish**: moved from "nice to have" to **MVP-tier** (Berlin demographics).

### Pivot 2026-04-30: dental clinics only

Restaurant and real-estate verticals were dropped to focus product +
sales effort on a single niche. The architecture (channel adapter,
classifier, tools layer) is generic enough to add other verticals back
in the future, but for now the seed data, demo sandbox, and prompt
language assume dental-clinic context.

## 4. Target niche

**Dental clinics in Berlin** (private + Kasse).

Use cases the bot must cover:
- Appointment booking (Kontrolle, Reinigung, Füllung, Bleaching, Implantate, Wurzelbehandlung).
- Reminders (T-24h / T-2h) via approved WhatsApp templates.
- Confirmations and rescheduling.
- No-show reduction (explicit confirm + auto re-book on cancel).
- FAQ and intake (insurance, Notfall, hours, address).
- Escalation to the practice manager when needed.

## 5. Conversation principles (NON-NEGOTIABLE)

1. Short messages.
2. One question at a time.
3. Natural, warm tone.
4. No corporate language.
5. No long forms in chat.
6. Emojis only if business config allows.
7. Never impersonate a specific human employee.
8. If asked, disclose AI status truthfully.
9. Escalate when sensitive.
10. Confirm important actions before executing.

**Bad**:
> Thank you for your message. In order to process your request, please provide
> date, time, number of guests, phone number, email address, and any
> additional information.

**Good**:
> Sure 😊 What day would you like to book for?

## 6. Human disclosure

Soft default opener:
> Hi, I'm Pantra, the assistant helping the team here.

If asked "are you a bot?":
> Yes, I'm an AI assistant helping the team reply faster. I can also pass this
> to a person if needed.

## 7. Human handoff triggers

Escalate when:

- Customer is angry / complaining.
- Discount or commercial negotiation.
- Legal / medical / financial questions.
- High-value bookings / events.
- Customer explicitly asks for a human.
- Classifier confidence is low.
- Calendar conflict cannot be resolved.
- Customer sends documents / sensitive info.
- Business has flagged the intent as human-only.

Handoff packet sent to Telegram + email contains: customer summary, last 10
messages, classifier output, suggested action, link to inbox view.

## 8. MVP scope

**Included**:
- WhatsApp Cloud API inbound + outbound (text + templates).
- PostgreSQL conversation storage (multi-tenant from day 1).
- Customer + conversation + message + booking + lead + handoff_task + ai_run models.
- Business config + knowledge base (DB-backed, simple JSON+text).
- Fast classifier (Anthropic Haiku 4.5 by default).
- Main conversation engine (Anthropic Sonnet 4.6 by default).
- Tool layer with idempotency + pessimistic locks.
- Google Calendar integration.
- Telegram + email handoff.
- T-24h / T-2h reminder workers.
- PII redaction for logs.
- Eval pipeline runner.
- AI usage / cost logging.

**Deferred to later phases**:
- Instagram channel.
- Admin dashboard (inbox, handoff queue, KB editor, analytics UI).
- Stripe billing.
- RAG with embeddings.
- Multi-location enterprise support.
- Mobile app, voice, payments.

## 9. Success criteria

The MVP is successful if it can:

- Receive and answer WhatsApp messages 24/7.
- Hold a natural conversation in DE / EN / ES / TR.
- Create a booking in Google Calendar via tool call.
- Create a lead summary.
- Hand off to a human via Telegram + email.
- Be configured for at least 3 business types.
- Log AI usage and cost.
- Be used by a real business for at least one week without engineering hand-holding.

## 10. Brand positioning

Use: **assistant**, **inbox**, **booking assistant**, **conversational assistant**.
Avoid: chatbot, bot, automation tool, AI gimmick.
