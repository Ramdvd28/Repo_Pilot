import os
import pytest
from app.core.config import normalize_database_url, settings
from app.core.database import _create_engine_and_session, is_serverless_env
from sqlalchemy.pool import NullPool


def test_normalize_database_url_postgresql_schemes():
    # Convert postgres:// to postgresql+asyncpg://
    raw = "postgres://user:pass@ep-cool.neon.tech:5432/neondb"
    normalized = normalize_database_url(raw)
    assert normalized == "postgresql+asyncpg://user:pass@ep-cool.neon.tech:5432/neondb"

    # Convert postgresql:// to postgresql+asyncpg://
    raw2 = "postgresql://user:pass@db.supabase.co:5432/postgres"
    normalized2 = normalize_database_url(raw2)
    assert normalized2 == "postgresql+asyncpg://user:pass@db.supabase.co:5432/postgres"


def test_normalize_database_url_sslmode_translation():
    # Translates sslmode=require to ssl=require for asyncpg
    raw = "postgres://user:pass@ep-cool.neon.tech/neondb?sslmode=require"
    normalized = normalize_database_url(raw)
    assert "ssl=require" in normalized
    assert "sslmode" not in normalized


def test_normalize_database_url_removes_unsupported_params():
    # Strips channel_binding, gssencmode, target_session_attrs which cause TypeError in asyncpg
    raw = "postgresql://user:pass@ep-cool.neon.tech/neondb?sslmode=require&channel_binding=require&target_session_attrs=read-write"
    normalized = normalize_database_url(raw)
    assert "channel_binding" not in normalized
    assert "target_session_attrs" not in normalized
    assert "ssl=require" in normalized


def test_normalize_database_url_preserves_sqlite():
    sqlite_url = "sqlite+aiosqlite:///storage/repopilot.db"
    assert normalize_database_url(sqlite_url) == sqlite_url

    tmp_sqlite = "sqlite+aiosqlite:////tmp/repopilot.db"
    assert normalize_database_url(tmp_sqlite) == tmp_sqlite


def test_serverless_engine_uses_nullpool(monkeypatch):
    monkeypatch.setenv("VERCEL", "1")
    assert is_serverless_env() is True

    # Engine for PostgreSQL in serverless should use NullPool
    eng, _ = _create_engine_and_session("postgresql+asyncpg://user:pass@localhost:5432/db")
    assert isinstance(eng.pool, NullPool)


def test_postgres_url_env_resolution(monkeypatch):
    # Tests that POSTGRES_URL (standard Vercel Postgres env var) is picked up
    monkeypatch.setenv("POSTGRES_URL", "postgres://vercel_user:secret@ep-cool.us-east-1.aws.neon.tech/verceldb?sslmode=require")
    monkeypatch.delenv("DATABASE_URL", raising=False)

    url = settings.async_database_url
    assert url.startswith("postgresql+asyncpg://")
    assert "ep-cool.us-east-1.aws.neon.tech" in url
    assert "ssl=require" in url

