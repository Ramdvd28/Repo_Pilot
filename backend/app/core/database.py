import os
from pathlib import Path
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
from app.core.config import settings


class Base(DeclarativeBase):
    pass


def is_serverless_env() -> bool:
    """Returns True if running in a serverless function environment (e.g. Vercel, AWS Lambda)."""
    return bool(
        os.environ.get("VERCEL")
        or os.environ.get("VERCEL_ENV")
        or os.environ.get("AWS_LAMBDA_FUNCTION_NAME")
    )


def _get_sqlite_url() -> str:
    if is_serverless_env():
        return "sqlite+aiosqlite:////tmp/repopilot.db"
    storage_dir = Path("storage").resolve()
    storage_dir.mkdir(parents=True, exist_ok=True)
    return f"sqlite+aiosqlite:///{storage_dir / 'repopilot.db'}"


def _create_engine_and_session(url: str):
    if url.startswith("sqlite"):
        eng = create_async_engine(
            url,
            echo=False,
            connect_args={"check_same_thread": False}
        )
    else:
        # Managed PostgreSQL configuration
        if is_serverless_env():
            # For serverless microVM containers (Vercel/Lambda), NullPool prevents connection leaks
            # across frozen/recycled instances, and timeout=15 allows managed databases (e.g. Neon)
            # sufficient headroom to resume from compute suspension.
            eng = create_async_engine(
                url,
                echo=False,
                poolclass=NullPool,
                connect_args={"timeout": 15.0}
            )
        else:
            eng = create_async_engine(
                url,
                echo=False,
                pool_pre_ping=True,
                pool_recycle=300,
                connect_args={"timeout": 10.0}
            )

    session_factory = async_sessionmaker(
        bind=eng,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )
    return eng, session_factory


engine, AsyncSessionLocal = _create_engine_and_session(settings.async_database_url)
_db_initialized = False


async def init_db() -> None:
    global engine, AsyncSessionLocal, _db_initialized
    is_serverless = is_serverless_env()
    current_url = settings.async_database_url

    if is_serverless and current_url.startswith("sqlite"):
        print(
            "[Database] WARNING: Running on Vercel serverless with ephemeral SQLite at /tmp/repopilot.db. "
            "Repository records will NOT survive across separate function instances or cold starts. "
            "Please configure a persistent managed PostgreSQL database (DATABASE_URL or POSTGRES_URL) "
            "in your Vercel project environment variables."
        )

    try:
        # Import models so Base.metadata is fully populated with all tables
        import app.models  # noqa: F401
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        _db_initialized = True
    except Exception as e:
        if is_serverless:
            # In serverless environments, DO NOT silently fall back to /tmp/repopilot.db!
            # Ephemeral SQLite masks the failure and causes repository records to disappear on subsequent requests.
            print(
                f"[Database] CRITICAL: Failed to connect or initialize managed PostgreSQL on Vercel: {e}. "
                f"Ephemeral SQLite fallback is strictly prohibited in serverless mode to prevent cross-instance data loss. "
                f"Please verify DATABASE_URL or POSTGRES_URL in your Vercel project settings."
            )
            raise
        else:
            # If connection to PostgreSQL failed in local development, fallback to local persistent SQLite
            if not current_url.startswith("sqlite"):
                print(f"[Database] Local PostgreSQL connection failed ({e}). Falling back to local SQLite database...")
                sqlite_url = _get_sqlite_url()
                engine, AsyncSessionLocal = _create_engine_and_session(sqlite_url)
                async with engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
                _db_initialized = True
                print("[Database] Successfully initialized fallback local SQLite database.")
            else:
                raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    global _db_initialized
    if not _db_initialized:
        try:
            await init_db()
        except Exception as e:
            print(f"[Database] Warning: auto init_db in get_db encountered: {e}")
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
