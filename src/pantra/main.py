from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from pantra.api.demo.router import router as demo_router
from pantra.api.webhooks.whatsapp import router as whatsapp_router
from pantra.config import settings
from pantra.logging import configure_logging, log

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    configure_logging()
    Path(settings.audio_storage_path).mkdir(parents=True, exist_ok=True)
    log.info("pantra.startup", env=settings.environment)
    yield
    log.info("pantra.shutdown")


app = FastAPI(
    title="Pantra",
    version="0.1.0",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
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
    "/static/audio",
    StaticFiles(directory=settings.audio_storage_path, check_dir=False),
    name="audio-static",
)

app.include_router(whatsapp_router, prefix="/webhooks", tags=["webhooks"])
app.include_router(demo_router, tags=["demo"])
