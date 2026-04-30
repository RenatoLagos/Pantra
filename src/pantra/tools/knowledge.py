from __future__ import annotations

import uuid

from pydantic import BaseModel, Field
from sqlalchemy import text

from pantra.models import KnowledgeCategory, Service
from pantra.tools.base import Tool, ToolContext

CATEGORY_CHOICES = tuple(c.value for c in KnowledgeCategory)


# ─── search_knowledge ───────────────────────────────────────────────────
class SearchKnowledgeIn(BaseModel):
    query: str = Field(description="The patient's question, verbatim or paraphrased.")
    language: str | None = Field(
        default=None,
        description="ISO 639-1 ('de' | 'en'). Defaults to the conversation language.",
    )
    category: str | None = Field(
        default=None,
        description=f"Optional filter. One of: {', '.join(CATEGORY_CHOICES)}.",
    )
    max_results: int = 5


class KnowledgeResult(BaseModel):
    id: uuid.UUID
    category: str
    title: str
    body: str


class SearchKnowledgeOut(BaseModel):
    results: list[KnowledgeResult]


class SearchKnowledgeTool(Tool[SearchKnowledgeIn, SearchKnowledgeOut]):
    name = "search_knowledge"
    description = (
        "Search the clinic's knowledge base (FAQs, policies, treatment "
        "details, insurance, pricing, practical info) using full-text "
        "search. Call this whenever the patient asks something not directly "
        "answerable from the snippets in your system prompt — pricing, "
        "insurance specifics, parking, hygiene protocols, post-care, etc."
    )
    input_model = SearchKnowledgeIn
    output_model = SearchKnowledgeOut

    async def _execute(
        self, ctx: ToolContext, payload: SearchKnowledgeIn
    ) -> SearchKnowledgeOut:
        # Postgres FTS with config 'simple' so DE + EN share one index without
        # needing per-language stemming. websearch_to_tsquery is forgiving with
        # natural-language queries.
        stmt = text(
            """
            SELECT
                id, category, title, body,
                ts_rank(
                    to_tsvector('simple', coalesce(title, '') || ' ' || coalesce(body, '')),
                    websearch_to_tsquery('simple', :q)
                ) AS rank
            FROM knowledge_entries
            WHERE business_id = :biz
              AND is_active = TRUE
              AND (CAST(:lang AS text) IS NULL OR language = :lang)
              AND (CAST(:cat  AS text) IS NULL OR category = :cat)
              AND to_tsvector('simple', coalesce(title, '') || ' ' || coalesce(body, ''))
                  @@ websearch_to_tsquery('simple', :q)
            ORDER BY rank DESC
            LIMIT :limit
            """
        )
        rows = (
            await ctx.session.execute(
                stmt,
                {
                    "biz": ctx.business_id,
                    "q": payload.query,
                    "lang": payload.language,
                    "cat": payload.category,
                    "limit": payload.max_results,
                },
            )
        ).mappings().all()

        return SearchKnowledgeOut(
            results=[
                KnowledgeResult(
                    id=r["id"],
                    category=r["category"],
                    title=r["title"],
                    body=r["body"],
                )
                for r in rows
            ]
        )


# ─── get_treatment_details ──────────────────────────────────────────────
class GetTreatmentDetailsIn(BaseModel):
    service_id: uuid.UUID
    language: str = Field(default="de", description="ISO 639-1 ('de' | 'en').")


class GetTreatmentDetailsOut(BaseModel):
    name: str
    duration_minutes: int
    price_eur: float | None = None
    description: str | None = None
    details_long: str | None = None
    pre_care: str | None = None
    post_care: str | None = None
    contraindications: str | None = None
    insurance_notes: str | None = None


class GetTreatmentDetailsTool(Tool[GetTreatmentDetailsIn, GetTreatmentDetailsOut]):
    name = "get_treatment_details"
    description = (
        "Fetch the long-form information about a specific treatment: full "
        "description, pre-care, post-care, contraindications, insurance "
        "coverage. Use when the patient asks 'how does X work?', 'what "
        "should I do before/after?', 'is it safe if I'm pregnant?', etc."
    )
    input_model = GetTreatmentDetailsIn
    output_model = GetTreatmentDetailsOut

    async def _execute(
        self, ctx: ToolContext, payload: GetTreatmentDetailsIn
    ) -> GetTreatmentDetailsOut:
        service = await ctx.session.get(Service, payload.service_id)
        if not service or service.business_id != ctx.business_id:
            return GetTreatmentDetailsOut(
                name="(unknown)",
                duration_minutes=0,
            )

        return GetTreatmentDetailsOut(
            name=service.localized_name(payload.language),
            duration_minutes=service.duration_minutes,
            price_eur=(service.price_cents / 100) if service.price_cents else None,
            description=service.description,
            details_long=service.localized("details_long", payload.language),
            pre_care=service.localized("pre_care", payload.language),
            post_care=service.localized("post_care", payload.language),
            contraindications=service.localized("contraindications", payload.language),
            insurance_notes=service.localized("insurance_notes", payload.language),
        )
