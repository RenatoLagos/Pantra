from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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

    llm_classifier_provider: Literal["anthropic", "gemini", "openai"] = "anthropic"
    llm_classifier_model: str = "claude-haiku-4-5-20251001"

    llm_main_provider: Literal["anthropic", "gemini", "openai"] = "anthropic"
    llm_main_model: str = "claude-sonnet-4-6"
    llm_main_max_tokens: int = 1024
    llm_main_temperature: float = 0.4

    # ─── Memory ──
    memory_window_messages: int = 20
    memory_summarize_after: int = 40

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

    audio_storage_path: str = "./storage/audio"
    audio_retention_hours: int = 24
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

    # ─── Privacy ──
    pii_redaction_enabled: bool = True
    log_retention_days: int = 7

    # ─── Calendar ──
    google_calendar_client_email: str = ""
    google_calendar_private_key: str = ""
    google_calendar_scopes: str = "https://www.googleapis.com/auth/calendar"


@lru_cache
def _load_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


settings: Settings = _load_settings()
