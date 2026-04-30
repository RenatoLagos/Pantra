from __future__ import annotations

import os

# Ensure tests run with a deterministic, non-secret env regardless of
# whatever .env the developer has lying around.
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://pantra:pantra@localhost:5432/pantra_test")
os.environ.setdefault("DATABASE_URL_SYNC", "postgresql+psycopg2://pantra:pantra@localhost:5432/pantra_test")
os.environ.setdefault("ANTHROPIC_API_KEY", "test")
os.environ.setdefault("PII_REDACTION_ENABLED", "true")
