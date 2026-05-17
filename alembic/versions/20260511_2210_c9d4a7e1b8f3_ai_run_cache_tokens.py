"""ai_run cache tokens — track Anthropic prompt-caching telemetry

Revision ID: c9d4a7e1b8f3
Revises: 8a72e4883e02
Create Date: 2026-05-11 22:10:00.000000

Adds two nullable Integer columns to `ai_runs` so we can persist the
cache_read_input_tokens and cache_creation_input_tokens that Anthropic
returns in every messages.create() response. Used by the cost-tracking
analytics layer (services/cost.py) to measure the real savings from
prompt caching (#5) and Haiku-first routing (#6).

Both columns are nullable: rows from before this migration and rows
written by non-caching providers (e.g. Gemini, OpenAI) leave them empty.
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c9d4a7e1b8f3"
down_revision: str | None = "8a72e4883e02"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("ai_runs", sa.Column("cache_read_tokens", sa.Integer(), nullable=True))
    op.add_column("ai_runs", sa.Column("cache_creation_tokens", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("ai_runs", "cache_creation_tokens")
    op.drop_column("ai_runs", "cache_read_tokens")
