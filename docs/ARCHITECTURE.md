# Pantra — Architecture

## 1. High-level flow

```
                ┌────────────────────────────┐
                │  WhatsApp Cloud API (Meta) │
                └─────────────┬──────────────┘
                              │  webhook
                              ▼
              ┌────────────────────────────────┐
              │   api/webhooks/whatsapp.py     │
              │  signature verify + dispatch   │
              └─────────────┬──────────────────┘
                            │  normalized message
                            ▼
                ┌──────────────────────────┐
                │  services/conversation   │
                │  persist + dispatch      │
                └──────────┬───────────────┘
                           ▼
              ┌──────────────────────────┐
              │   llm/classifier.py      │  ← Haiku 4.5
              │ language / intent / etc. │
              └──────────┬───────────────┘
                         ▼
              ┌──────────────────────────┐
              │   llm/engine.py          │  ← Sonnet 4.6
              │ system prompt + memory + │
              │ tool-use loop            │
              └──────────┬───────────────┘
                         ▼
              ┌──────────────────────────┐
              │   tools/booking, lead,   │
              │   handoff, email, ...    │
              └──────────┬───────────────┘
                         ▼
              ┌──────────────────────────┐
              │  channels/whatsapp/      │
              │  send + window check +   │
              │  template fallback       │
              └──────────────────────────┘
```

## 2. Layering rules

- **API** depends on **services**, never on **models** or **channels** directly.
- **services** orchestrate **llm + tools + channels**.
- **llm** never imports **models** or **db** — receives pre-shaped data.
- **tools** are the ONLY layer that mutates business state (bookings, leads).
- **handoff** + **workers** can call services, but never the LLM directly.

If a layer pulls in something to its left in this list, it's a smell:

```
api  >  services  >  (llm | tools | channels)  >  models / db
```

## 3. The LLM is sandboxed

The conversation engine emits **structured tool calls** that the backend
executes. The LLM does not write SQL, does not call external APIs, does not
have database credentials.

Every tool:

- Has a Pydantic input schema and a Pydantic output schema.
- Is **idempotent** by `(business_id, tool_name, idempotency_key)`.
- Uses **pessimistic locks** when mutating contended resources (booking slots).
- Validates business config before mutation (e.g. opening hours).
- Returns a structured result the engine can verbalize.

## 4. Concurrency: bookings

Two customers, same slot, same instant. The flow:

1. `check_availability` reads with `SELECT … FOR UPDATE` inside a transaction.
2. The same transaction calls `create_booking` if the slot is free.
3. The transaction commits — or rolls back if conflict.
4. The tool layer recognises a unique-violation on `(business_id, date, time, resource_id)` and returns `slot_taken`.
5. The engine apologises and proposes another slot.

Idempotency key: `whatsapp:{message_id}` so a re-delivered webhook never
double-books.

## 5. WhatsApp 24h conversation window

WhatsApp's "customer service window" closes 24h after the last customer
message. After that, only approved **template messages** can be sent.

Implementation:

- `channels/whatsapp/window.py` keeps a per-conversation `last_inbound_at`.
- Before sending free text, the adapter calls `is_within_24h(conversation)`.
- Outside the window, the adapter looks up an approved template by name from
  `channels/whatsapp/templates.py` and renders it with parameters.
- A template registry tracks status: `draft → submitted → approved → rejected`.
- Reminder workers always send via templates (they're scheduled outside the
  window by definition).

## 6. Conversation memory

Three layers, each with a different lifetime:

| Layer | Lifetime | Storage | Used for |
|-------|----------|---------|----------|
| Sliding window | last N messages | DB query at request time | exact recent context |
| Rolling summary | full conversation | `conversations.summary` (text) | long-term thread coherence |
| Structured customer memory | across conversations | `customers.notes` JSONB | preferences, prior bookings, language, dietary, etc. |

When the message count crosses a threshold (`MEMORY_SUMMARIZE_AFTER`), a
worker job re-summarises the older half and trims the window.

## 7. Privacy & logging

- All inbound text is passed through `privacy/pii.py` before being written to
  prompt logs (redacts emails, phones, IBAN, IDs).
- Prompt logs (`ai_runs.classifier_output`, full prompts) live for
  `LOG_RETENTION_DAYS` (default 7).
- The customer-facing transcript (`messages.text`) is kept for the
  conversation lifetime but is **not** the same store as prompt logs.
- Customers can opt out → `customers.opted_out = true` blocks all outbound +
  triggers handoff.

## 8. Handoff (Telegram + email, no dashboard)

`handoff_to_human` tool ⟶ `handoff/telegram.py` pushes a notification to
the business owner's Telegram chat (created via `@BotFather`) with the
reason, priority, business + conversation IDs, and a short summary.
HTML parse mode is used so message text is escaped via `html.escape`.

`handoff/email.py` sends the same payload to the business email when
Telegram isn't configured (or as a second channel for redundancy).

`handoff/__init__.dispatch()` is the single entry point: it dispatches
to whatever transports are configured and warns when none is. New
transports (e.g. a generic webhook for Zapier / n8n) plug into the same
function.

MVP keeps the bot token + chat_id in env. Phase 2 moves `chat_id` to
`business.config` so each tenant points to their own owner chat.

## 9. Eval pipeline

`evals/runner.py` loads case files (`evals/cases/*.yaml`), runs them through
the classifier + engine with mocked tools, and emits a JSON report. Each
case asserts:

- Detected language.
- Detected intent.
- Tool calls (set + order).
- Final reply matches a list of expected substrings or a regex.
- Latency / token budget bounds.

Run on every prompt or model change. CI gate before merging prompt edits.

## 10. Multi-tenancy

Every row carries `business_id`. Every service / tool / API endpoint
**requires** a `business_id` in scope. Webhook dispatch resolves
`business_id` from the receiving phone number ID.

There is no global "admin" entity in MVP — operators access data by directly
querying the DB or via the future dashboard.

## 11. Configurability

All model names, prompt templates, retention values, thresholds, and
provider URLs live in environment variables (loaded via
`pydantic-settings`). No model name is hardcoded in source.

## 12. What we are NOT building (yet)

- A chatbot builder.
- A workflow editor.
- A no-code admin UI.
- A multi-region deployment.
- A campaign / marketing module.

If a future ticket asks for any of these, push back and keep the product
focused on conversational AI for local businesses.
