# Pantra

Multilingual AI conversational assistant **for dental clinics** in Berlin.
Manages WhatsApp messages with a natural, human-like tone — connected to
appointment booking, reminders, calendar, and human handoff.

> **MVP scope**: dental clinics only. WhatsApp + web sandbox.
> Telegram/email handoff (no admin dashboard).
> Single classifier + single main LLM. DE / EN / ES / TR.

See [`docs/PROJECT_SPEC.md`](docs/PROJECT_SPEC.md) for the product spec
and [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for technical decisions.

## Stack

- **Backend**: FastAPI (Python 3.12+)
- **DB**: PostgreSQL + SQLAlchemy 2 (async) + Alembic
- **Cache / queue**: Redis + Celery
- **LLM**: Anthropic (classifier + main) — configurable via env
- **Channel**: WhatsApp Cloud API (Meta) or 360dialog — adapter-pluggable
- **Handoff**: Telegram bot + transactional email (Resend / SES)

## Layout

```
src/pantra/
  api/           HTTP entrypoints (webhooks + REST routes)
  channels/      Channel adapters (whatsapp/...)
  llm/           Classifier, engine, memory, prompts
  tools/         Actions the LLM can call (booking, lead, handoff, ...)
  models/        SQLAlchemy ORM models
  services/      Business logic
  handoff/       Telegram + email senders
  privacy/       PII redaction
  workers/       Celery tasks (reminders, ...)
  evals/         LLM eval pipeline
```

## Quick start (dev)

```bash
# 1. Install
python -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'

# 2. Configure
cp .env.example .env
# fill in DATABASE_URL, REDIS_URL, ANTHROPIC_API_KEY,
# WHATSAPP_* and at least one of TELEGRAM_BOT_TOKEN+TELEGRAM_CHAT_ID / RESEND_API_KEY

# 3. DB
alembic upgrade head

# 4. Run
uvicorn pantra.main:app --reload
# in another shell:
celery -A pantra.workers.celery_app worker -l info
celery -A pantra.workers.celery_app beat -l info
```

## Webhook (Meta verification)

Point the WhatsApp Cloud API webhook to `POST /webhooks/whatsapp` and the
verification GET to the same path. The `WHATSAPP_VERIFY_TOKEN` and
`WHATSAPP_APP_SECRET` envs validate the handshake and signatures.

## Demo sandbox

Pantra ships with a public web sandbox at `/demo` (dental clinic).
Audios work both ways: the prospect can record a voice note, the bot
transcribes it, replies, and (if `tts_mode=mirror`) sends an audio
reply back.

```bash
# 1. Seed the demo business (idempotent)
python -m scripts.seed_demos

# 2. Populate practitioners + services + 1 year of agenda
python -m scripts.seed_dental_clinic

# 3. Open in your browser
open http://localhost:8001/demo
```

Demo conversations are isolated from production by `is_demo=True` on
every row. They never trigger real Telegram/email handoffs unless
`DEMO_HANDOFF_TELEGRAM_CHAT_ID` is set (separate chat for prospect tests).

## Tests & evals

```bash
pytest
python -m pantra.evals.runner       # run conversation eval cases
```
