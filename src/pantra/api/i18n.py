"""Landing i18n — central translation catalog + shared Jinja renderer.

Marketing copy lives in per-locale JSON under
``templates/landing/i18n/<lang>/<namespace>.json``, keyed by dotted paths
(e.g. ``common.nav.features``). Templates call ``{{ t('common.nav.features') }}``;
the ``t`` global resolves the active language from the render context's
``html_lang`` and falls back to the default language, then to the raw key so
missing strings are visible during review rather than rendering blank.

Both the landing and legal routers share the single ``templates`` instance and
``render`` helper defined here, so ``t`` is available everywhere and the
language-resolution rules stay in one place.
"""
from __future__ import annotations

import json
from pathlib import Path

from fastapi import Request
from fastapi.templating import Jinja2Templates
from jinja2 import pass_context

TEMPLATES_DIR = Path(__file__).resolve().parents[3] / "templates"
CATALOG_DIR = TEMPLATES_DIR / "landing" / "i18n"

# Ship languages. German is primary (the clinics are German, SEO targets DE);
# English is the alternate. Spanish was only ever a founder-review placeholder
# and is intentionally not shipped.
SUPPORTED_LANGS: tuple[str, ...] = ("de", "en")
DEFAULT_LANG = "de"

# schema.org / OpenGraph locale codes per ship language.
OG_LOCALE = {"de": "de_DE", "en": "en_US"}


def _load_catalog() -> dict[str, dict]:
    """Load every ``<lang>/<namespace>.json`` into ``catalog[lang][namespace]``."""
    catalog: dict[str, dict] = {}
    for lang in SUPPORTED_LANGS:
        merged: dict[str, dict] = {}
        lang_dir = CATALOG_DIR / lang
        if lang_dir.is_dir():
            for path in sorted(lang_dir.glob("*.json")):
                merged[path.stem] = json.loads(path.read_text(encoding="utf-8"))
        catalog[lang] = merged
    return catalog


_CATALOG = _load_catalog()


def translate(lang: str, key: str) -> str:
    """Resolve a dotted ``key`` for ``lang``, falling back to DE, then the key."""
    for candidate in (lang, DEFAULT_LANG):
        node: object = _CATALOG.get(candidate)
        for part in key.split("."):
            if isinstance(node, dict) and part in node:
                node = node[part]
            else:
                node = None
                break
        if isinstance(node, str):
            return node
    return key  # last resort: surface the missing key instead of blank text


def resolve_lang(request: Request) -> str:
    """Pick the language: explicit ``?lang=`` → cookie → Accept-Language → default."""
    requested = request.query_params.get("lang")
    if requested and requested.lower() in SUPPORTED_LANGS:
        return requested.lower()

    cookie = request.cookies.get("lang")
    if cookie and cookie.lower() in SUPPORTED_LANGS:
        return cookie.lower()

    for part in request.headers.get("accept-language", "").split(","):
        code = part.split(";")[0].strip().lower()[:2]
        if code in SUPPORTED_LANGS:
            return code

    return DEFAULT_LANG


templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@pass_context
def _t(context: dict, key: str) -> str:
    return translate(context.get("html_lang") or DEFAULT_LANG, key)


templates.env.globals["t"] = _t
templates.env.globals["OG_LOCALE"] = OG_LOCALE
templates.env.globals["SUPPORTED_LANGS"] = SUPPORTED_LANGS


def render(
    request: Request,
    template_name: str,
    *,
    lang: str | None = None,
    **extra: object,
):
    """Render a template with i18n context.

    ``lang`` forces a language (used by the German-only legal pages); when left
    ``None`` the language is resolved from the request and, if the visitor set
    it explicitly via ``?lang=``, persisted in a cookie so it sticks across pages.
    """
    resolved = lang or resolve_lang(request)
    response = templates.TemplateResponse(
        request, template_name, {"html_lang": resolved, **extra}
    )
    if lang is None and request.query_params.get("lang"):
        response.set_cookie(
            "lang", resolved, max_age=180 * 86400, samesite="lax", httponly=False
        )
    return response
