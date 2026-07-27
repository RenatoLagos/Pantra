from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _is_change_me_placeholder(value: str) -> bool:
    """Detect the placeholder family used by checked-in environment examples."""
    normalized = value.strip().lower()
    return not normalized or normalized.startswith("change-me")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ─── Runtime ──
    environment: Literal["development", "staging", "production"] = "development"
    log_level: str = "INFO"
    timezone: str = "Europe/Berlin"

    # ─── Database ──
    database_url: str = Field(..., description="asyncpg URL used by the app")
    database_url_sync: str = Field(..., description="psycopg2 URL used by Alembic")

    # ─── Redis / Celery ──
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # ─── WhatsApp ──
    whatsapp_provider: Literal["cloud_api", "360dialog"] = "cloud_api"
    whatsapp_access_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_business_account_id: str = ""
    whatsapp_verify_token: str = "change-me"
    whatsapp_app_secret: str = ""
    whatsapp_api_base: str = "https://graph.facebook.com/v21.0"

    # ─── LLM ──
    anthropic_api_key: str = ""
    gemini_api_key: str = ""
    openai_api_key: str = ""

    # ─── Realtime voice ──
    # Webhook ingestion and call acceptance are separate switches. The pilot's
    # deduplication is process-local, so enabling ingestion requires an explicit
    # single-worker acknowledgement until a shared store is implemented.
    voice_webhook_enabled: bool = False
    voice_webhook_single_worker: bool = False
    voice_webhook_max_body_bytes: int = 64 * 1024
    voice_enabled: bool = False
    openai_webhook_secret: str = ""
    voice_realtime_model: str = "gpt-realtime"
    voice_realtime_voice: str = "marin"
    voice_api_timeout_seconds: float = 5.0
    voice_realtime_instructions: str = (
        "You are Pantra, a friendly dental clinic receptionist. "
        "Speak naturally and help with general administrative questions."
    )

    llm_classifier_provider: Literal["anthropic", "gemini", "openai"] = "anthropic"
    llm_classifier_model: str = "claude-haiku-4-5-20251001"

    llm_main_provider: Literal["anthropic", "gemini", "openai"] = "anthropic"
    llm_main_model: str = "claude-sonnet-4-6"
    llm_main_max_tokens: int = 1024
    llm_main_temperature: float = 0.4

    # Per-request timeout (seconds) and bounded retries for LLM calls. Keeps a
    # hung upstream call from holding a DB session open for the SDK default
    # (~10 min); the SDK honors Retry-After on 429 and backs off on 5xx.
    llm_timeout_seconds: float = Field(default=30.0, gt=0)
    llm_max_retries: int = Field(default=3, ge=0)

    # ─── Memory ──
    memory_window_messages: int = 20

    # ─── Reminders ──
    # A booking is reminded when its appointment instant (computed in the
    # business timezone) falls within ± this many seconds of the target lead
    # time. Must exceed half the beat interval (60s) so no booking is missed;
    # idempotency (sent_reminders) makes a generous window safe.
    reminder_window_seconds: int = 90

    # ─── Handoff ──
    # Telegram bot for the business owner. MVP keeps a single bot + chat_id
    # in env; Phase 2 will move chat_id to business.config (multi-tenant).
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    telegram_api_base: str = "https://api.telegram.org"

    handoff_email_to: str = ""
    handoff_email_from: str = "pantra@example.com"
    email_provider: Literal["resend", "ses", "smtp"] = "resend"
    resend_api_key: str = ""

    # ─── Audio ──
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"      # Rachel (multilingual)
    elevenlabs_model_id: str = "eleven_turbo_v2_5"          # multilingual + low latency
    elevenlabs_api_base: str = "https://api.elevenlabs.io/v1"

    # Speech-to-text (Whisper) call: per-request timeout + bounded retries.
    # Kept separate from the chat LLM knobs so STT (which can run longer on
    # bigger recordings) can be tuned independently.
    stt_timeout_seconds: float = Field(default=30.0, gt=0)
    stt_max_retries: int = Field(default=3, ge=0)

    audio_storage_path: str = "./storage/audio"
    # Inbound recordings (raw patient voice — sensitive PII) are stored OUTSIDE
    # audio_storage_path so they are never reachable via the /static/audio mount.
    # Kept as a sibling directory; the audio retention worker sweeps both.
    audio_inbound_path: str = "./storage/audio_inbound"
    audio_retention_hours: int = 24
    # Hard cap on an inbound demo audio upload. Guards the public, unauthenticated
    # demo endpoint against disk-fill / memory-pressure abuse.
    demo_audio_max_bytes: int = 15 * 1024 * 1024  # 15 MB
    # Bounded allowance for multipart boundaries and form-field headers. The ASGI
    # guard caps the whole request at file limit + this overhead.
    demo_audio_multipart_overhead_bytes: int = 64 * 1024
    # Public base URL for audio served from filesystem. Required for
    # WhatsApp send_audio (Meta needs an HTTPS URL it can fetch).
    # Example dev: https://<ngrok>.ngrok.app/static/audio
    # Example prod: https://app.pantra.com/static/audio
    audio_public_url_base: str = ""

    # tts_default_mode: text_only | mirror | audio_always (overridable per business)
    tts_default_mode: Literal["text_only", "mirror", "audio_always"] = "mirror"

    # ─── Demo ──
    # Optional separate Telegram chat for demo handoffs (so prospect tests
    # don't notify the prod owner). When empty, demo handoffs are logged only.
    demo_handoff_telegram_chat_id: str = ""
    # Demo session lifetime (browser cookie + DB conversation purge).
    demo_session_days: int = 7
    # Abuse limits for the public, unauthenticated demo endpoints. Demos bypass
    # per-business quota (their cost is marketing), so these ceilings are the
    # only thing standing between an anonymous script and the LLM cost budget.
    # 32 KiB permits the schema's maximum text/session payload even when a JSON
    # client emits worst-case escaped Unicode, while still bounding pre-parse work.
    demo_message_max_body_bytes: int = 32 * 1024
    demo_rate_per_minute: int = 10  # per client IP, fixed window
    demo_daily_cap: int = 60  # per client IP and demo session, rolling 24h
    # Public demo rate limiting fails open, so Redis connection/read failures
    # must resolve quickly rather than tying up unauthenticated requests.
    demo_ratelimit_redis_timeout_seconds: float = 0.5

    # ─── Privacy ──
    pii_redaction_enabled: bool = True
    log_retention_days: int = 7

    # ─── Admin ──
    # Shared bearer token guarding /admin/* endpoints (usage analytics,
    # quota management, etc.). MUST be set in production; empty default
    # locks the admin surface so a forgotten secret never accidentally
    # exposes data.
    admin_token: str = ""

    # ─── Calendar ──
    google_calendar_client_email: str = ""
    google_calendar_private_key: str = ""
    google_calendar_scopes: str = "https://www.googleapis.com/auth/calendar"


    @model_validator(mode="after")
    def _require_production_secrets(self) -> Settings:
        """Fail fast (refuse to boot) when production is missing a security-critical
        secret. Prevents insecure-by-default deploys — e.g. an empty app secret that
        would silently disable webhook signature verification."""
        problems: list[str] = []
        if self.voice_enabled and not self.voice_webhook_enabled:
            problems.append("VOICE_WEBHOOK_ENABLED is required when realtime voice is enabled")
        if self.voice_webhook_enabled and not self.openai_api_key:
            problems.append("OPENAI_API_KEY is required when the voice webhook is enabled")
        if self.voice_webhook_enabled and not self.openai_webhook_secret:
            problems.append("OPENAI_WEBHOOK_SECRET is required when the voice webhook is enabled")
        if self.voice_webhook_enabled and not self.voice_webhook_single_worker:
            problems.append(
                "VOICE_WEBHOOK_SINGLE_WORKER=true is required for in-memory webhook idempotency"
            )
        if self.voice_webhook_max_body_bytes <= 0:
            problems.append("VOICE_WEBHOOK_MAX_BODY_BYTES must be greater than zero")
        if self.voice_api_timeout_seconds <= 0:
            problems.append("VOICE_API_TIMEOUT_SECONDS must be greater than zero")

        if self.environment != "production":
            if problems:
                raise ValueError("Invalid voice configuration:\n  - " + "\n  - ".join(problems))
            return self

        if _is_change_me_placeholder(self.whatsapp_app_secret):
            problems.append(
                "WHATSAPP_APP_SECRET must be changed from its placeholder in production "
                "(webhook HMAC verification)"
            )
        if _is_change_me_placeholder(self.whatsapp_verify_token):
            problems.append("WHATSAPP_VERIFY_TOKEN must be changed from its placeholder")
        if self.llm_main_provider == "anthropic" and not self.anthropic_api_key.strip():
            problems.append("ANTHROPIC_API_KEY is required when the main LLM provider is anthropic")
        if self.llm_classifier_provider == "anthropic" and not self.anthropic_api_key.strip():
            problems.append(
                "ANTHROPIC_API_KEY is required when the classifier provider is anthropic"
            )
        if problems:
            raise ValueError("Insecure production configuration:\n  - " + "\n  - ".join(problems))
        return self


@lru_cache
def _load_settings() -> Settings:
    return Settings()


settings: Settings = _load_settings()
