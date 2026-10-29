import os
from pathlib import Path
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings


class Base(DeclarativeBase):
    pass


def _get_sqlite_url() -> str:
    if os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
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
        eng = create_async_engine(
            url,
            echo=False,
            pool_pre_ping=True,
            connect_args={"timeout": 3.0}
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
    try:
        # Import models so Base.metadata is fully populated with all tables
        import app.models  # noqa: F401
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        _db_initialized = True
    except Exception as e:
        # If connection to PostgreSQL failed, fallback to SQLite automatically
        if not settings.async_database_url.startswith("sqlite"):
            print(f"[Database] PostgreSQL connection failed ({e}). Falling back to SQLite database...")
            sqlite_url = _get_sqlite_url()
            engine, AsyncSessionLocal = _create_engine_and_session(sqlite_url)
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            _db_initialized = True
            print("[Database] Successfully initialized fallback SQLite database.")
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

