from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from pantra.api.admin.router import router as admin_router
from pantra.api.demo.body_limit import DemoRequestGuardMiddleware
from pantra.api.demo.router import router as demo_router
from pantra.api.landing.router import router as landing_router
from pantra.api.leads.router import router as leads_router
from pantra.api.legal.router import router as legal_router
from pantra.api.webhooks.openai_realtime import (
    create_voice_gateway,
)
from pantra.api.webhooks.openai_realtime import (
    router as openai_realtime_router,
)
from pantra.api.webhooks.whatsapp import router as whatsapp_router
from pantra.config import settings
from pantra.logging import configure_logging, log

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    Path(settings.audio_storage_path).mkdir(parents=True, exist_ok=True)
    voice_gateway = None
    if settings.voice_webhook_enabled:
        voice_gateway = create_voice_gateway()
        app.state.voice_gateway = voice_gateway
    log.info("pantra.startup", env=settings.environment)
    try:
        yield
    finally:
        if voice_gateway is not None:
            await voice_gateway.close()
        log.info("pantra.shutdown")


app = FastAPI(
    title="Pantra",
    version="0.1.0",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)
app.add_middleware(
    DemoRequestGuardMiddleware,
    message_max_body_bytes=settings.demo_message_max_body_bytes,
    audio_max_file_bytes=settings.demo_audio_max_bytes,
    multipart_overhead_bytes=settings.demo_audio_multipart_overhead_bytes,
    rate_per_minute=settings.demo_rate_per_minute,
    daily_cap=settings.demo_daily_cap,
)


@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    return RedirectResponse(url="/demo")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "env": settings.environment}


# Serve static assets (chat UI + generated audio).
app.mount(
    "/static/demo",
    StaticFiles(directory=str(PROJECT_ROOT / "static" / "demo")),
    name="demo-static",
)
app.mount(
    "/static/landing",
    StaticFiles(directory=str(PROJECT_ROOT / "static" / "landing")),
    name="landing-static",
)
app.mount(
    "/static/audio",
    StaticFiles(directory=settings.audio_storage_path, check_dir=False),
    name="audio-static",
)

app.include_router(whatsapp_router, prefix="/webhooks", tags=["webhooks"])
app.include_router(openai_realtime_router, prefix="/webhooks", tags=["webhooks"])
app.include_router(demo_router, tags=["demo"])
app.include_router(landing_router, tags=["landing"])
app.include_router(leads_router, tags=["leads"])
app.include_router(legal_router, tags=["legal"])
app.include_router(admin_router)
