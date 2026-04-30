# ADR 0001 — MVP scope and stack

- Date: 2026-04-27
- Status: Accepted

## Context

Greenfield project. Spec v1 left several decisions open: backend language,
channel scope at MVP, admin dashboard scope, LLM routing tiers, and the
handling of WhatsApp's 24h window, concurrency, eval, and privacy concerns.

## Decisions

1. **Backend stack: FastAPI + Python 3.12**, SQLAlchemy 2 async, Alembic,
   Celery + Redis, structlog. PostgreSQL.

2. **Channel scope at MVP: WhatsApp only.** Instagram is deferred to
   Phase 2 — the channel adapter abstraction (`channels/whatsapp/...`)
   is shaped so that an `instagram/` sibling will plug in cleanly.

3. **Handoff via Telegram bot + email; no admin dashboard at MVP.**
   The bot is created via `@BotFather`; the owner sends `/start` to it
   and we record the chat_id. Telegram gives instant push to the
   owner's phone, gratis, with a setup of seconds. Email runs as
   secondary channel. The full dashboard is Phase 2; that's where a
   generic webhook transport (Zapier/n8n) will also be wired.

4. **LLM stack: 1 classifier + 1 main model.** Defaults: Anthropic
   Haiku 4.5 for classifier, Anthropic Sonnet 4.6 for main. Multi-tier
   routing is deferred until we have real cost / quality data.

5. **Booking concurrency**: idempotency keys on every tool call,
   `SELECT FOR UPDATE` inside the transaction that performs the
   `check_availability` + `create_booking` pair, and a unique
   constraint on `(business_id, resource_id, date, time)` as the
   safety net.

6. **WhatsApp 24h window**: outbound free text only inside the window;
   outside, fall back to approved templates from a parametrized
   registry. A worker triggers reminders via templates.

7. **Memory model**: sliding window of last N messages + rolling
   summary on the conversation + structured customer memory in
   `customers.notes` JSONB.

8. **Eval pipeline**: case-based runner under `src/pantra/evals/`,
   loading YAML cases, run on every prompt change.

9. **Privacy**: PII redaction (regex-based) before any prompt is
   logged; 7-day retention for prompt logs; customer opt-out flag.

10. **Languages MVP**: DE, EN, ES, TR — Turkish promoted from "nice to
    have" because of Berlin's demographics.

11. **Niche pivot (2026-04-30)**: focus on **dental clinics only**.
    Restaurant and real-estate verticals were dropped to concentrate
    product + sales effort. The architecture stays generic (channels,
    LLM, tools) so other verticals can be reintroduced later if a
    second market is validated.

## Consequences

- The codebase is Python-only; if we later want a Node frontend it
  consumes the FastAPI REST.
- Phase 2 work is well-scoped: Instagram adapter, dashboard, possibly
  multi-tier LLM routing.
- The team needs to commit to the WhatsApp Business / Cloud API
  application process now (template approvals can take days to weeks).
- Eval cases must be authored alongside prompt work — engineering
  discipline, not a "later" task.
