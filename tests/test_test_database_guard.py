from __future__ import annotations

import pytest


@pytest.mark.parametrize(
    "url",
    [
        "postgresql+asyncpg://pantra:secret@localhost:5432/pantra",
        "postgresql+asyncpg://test:secret@localhost:5432/production",
        "postgresql+asyncpg://pantra:secret@localhost:5432/contest",
        "postgresql+asyncpg://pantra:secret@localhost:5432/production?application_name=test",
    ],
)
def test_database_guard_rejects_non_test_databases(url, database_url_guard):
    with pytest.raises(RuntimeError, match="Refusing test DDL"):
        database_url_guard(url)


@pytest.mark.parametrize(
    "url",
    [
        "postgresql+asyncpg://pantra:pantra@localhost:5432/pantra_test",
        "postgresql+asyncpg://pantra:pantra@localhost:5432/test_pantra",
        "postgresql+asyncpg://pantra:pantra@localhost:5432/test",
    ],
)
def test_database_guard_accepts_explicit_test_database(url, database_url_guard):
    database_url_guard(url)
