from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from pantra.config import settings

Provider = Literal["anthropic", "gemini", "openai"]
Role = Literal["classifier", "main", "summarizer", "fast_reply"]


@dataclass(frozen=True, slots=True)
class ModelChoice:
    role: Role
    provider: Provider
    model: str


def choose(role: Role) -> ModelChoice:
    """Resolve which model to use for a given role.

    MVP: 1 classifier (Haiku) + 1 main (Sonnet). The summariser and the
    fast_reply smalltalk path piggy-back on the classifier tier — same
    model, different system prompt — to keep cost and latency low for
    workloads that don't need tools or deep reasoning.
    """
    if role in ("classifier", "summarizer", "fast_reply"):
        return ModelChoice(
            role=role,
            provider=settings.llm_classifier_provider,
            model=settings.llm_classifier_model,
        )
    if role == "main":
        return ModelChoice(
            role=role,
            provider=settings.llm_main_provider,
            model=settings.llm_main_model,
        )
    raise ValueError(f"unknown role: {role}")
