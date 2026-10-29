import os
from pathlib import Path
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings


class Base(DeclarativeBase):
    pass


def _get_sqlite_url() -> str:
    if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
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
            pool_pre_ping=True
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


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    global engine, AsyncSessionLocal
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        # If connection to PostgreSQL failed, fallback to SQLite automatically
        if not settings.async_database_url.startswith("sqlite"):
            print(f"[Database] PostgreSQL connection failed ({e}). Falling back to SQLite database...")
            sqlite_url = _get_sqlite_url()
            engine, AsyncSessionLocal = _create_engine_and_session(sqlite_url)
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("[Database] Successfully initialized fallback SQLite database.")
        else:
            raise
