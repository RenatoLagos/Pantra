# Realtime voice pilot

The pilot exposes `POST /webhooks/openai/realtime` for signed OpenAI
`realtime.call.incoming` events. It can accept a call into a spoken Realtime
session, but it does not expose booking tools yet.

## Runtime contract

`VOICE_WEBHOOK_ENABLED=true` requires all of the following:

- `OPENAI_API_KEY`
- `OPENAI_WEBHOOK_SECRET`
- `VOICE_WEBHOOK_SINGLE_WORKER=true`

Webhook ingestion and call acceptance are separate. With the webhook enabled
and `VOICE_ENABLED=false`, Pantra still verifies the event and rejects the SIP
call through OpenAI. Therefore the disabled acceptance path also needs valid
OpenAI credentials.

The current deduplication store is intentionally process-local. Run **exactly
one application worker**. It is not durable, resets on restart, and does not
coordinate replicas. Replace it with Redis or PostgreSQL idempotency before
running multiple workers.

The endpoint caps request bodies, including chunked bodies, at
`VOICE_WEBHOOK_MAX_BODY_BYTES` and disables SDK retries. For OpenAI call-action
failures, an `x-should-retry: true` or `x-should-retry: false` response header
takes precedence. Without that override, connection failures, timeouts, HTTP
408, 409, 429, and 5xx responses are retryable and Pantra returns HTTP 503.
Other 4xx responses are treated as permanent and acknowledged once. OpenAI may
retry any non-2xx webhook delivery for up to 72 hours.
