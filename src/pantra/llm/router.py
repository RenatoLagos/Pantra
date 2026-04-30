from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from pantra.config import settings

Provider = Literal["anthropic", "gemini", "openai"]
Role = Literal["classifier", "main", "summarizer"]


@dataclass(frozen=True, slots=True)
class ModelChoice:
    role: Role
    provider: Provider
    model: str


def choose(role: Role) -> ModelChoice:
    """Resolve which model to use for a given role.

    MVP: 1 classifier + 1 main + summariser piggy-backs on classifier.
    No multi-tier routing — that's a Phase-2 decision driven by real cost
    and quality data.
    """
    if role == "classifier" or role == "summarizer":
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
