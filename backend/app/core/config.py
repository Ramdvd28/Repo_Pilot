import os
import json
from typing import List, Optional, Union
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def normalize_database_url(raw_url: str) -> str:
    """
    Normalizes database connection strings for SQLAlchemy + asyncpg:
    - Converts postgres:// and postgresql:// schemes to postgresql+asyncpg://
    - Translates sslmode parameter into asyncpg's expected ssl parameter
    - Strips unsupported asyncpg query parameters (channel_binding, gssencmode, target_session_attrs)
      that cause TypeError: connect() got an unexpected keyword argument in asyncpg
    """
    if not raw_url:
        return raw_url

    clean = raw_url.strip().strip("'\"")

    # Convert schemes to postgresql+asyncpg
    if clean.startswith("postgres://"):
        clean = "postgresql+asyncpg://" + clean[11:]
    elif clean.startswith("postgresql://"):
        clean = "postgresql+asyncpg://" + clean[13:]

    # Parse and clean query parameters for postgresql+asyncpg
    if clean.startswith("postgresql+asyncpg://"):
        parsed = urlparse(clean)
        query = parse_qs(parsed.query)

        # Convert sslmode to ssl for asyncpg
        if "sslmode" in query:
            mode = query.pop("sslmode")[0].lower()
            if mode in ("require", "prefer", "verify-ca", "verify-full"):
                query["ssl"] = ["require"]
            elif mode in ("disable", "allow"):
                query["ssl"] = ["false"]

        # Remove asyncpg-incompatible libpq parameters
        for unsupp in ("channel_binding", "gssencmode", "target_session_attrs"):
            query.pop(unsupp, None)

        new_query = urlencode(query, doseq=True)
        clean = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))

    return clean


class Settings(BaseSettings):
    PROJECT_NAME: str = "RepoPilot AI"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # CORS
    BACKEND_CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str) and v.startswith("["):
            return json.loads(v)
        return v

    # Database Configuration
    POSTGRES_USER: str = "repopilot"
    POSTGRES_PASSWORD: str = "repopilot_password"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "repopilot_db"
    
    # Supported managed PostgreSQL environment variable names (Neon, Supabase, Vercel Postgres, AWS RDS)
    DATABASE_URL: Optional[str] = None
    POSTGRES_URL: Optional[str] = None
    POSTGRES_PRISMA_URL: Optional[str] = None
    POSTGRES_URL_NON_POOLING: Optional[str] = None

    @property
    def async_database_url(self) -> str:
        # Check all standard PostgreSQL environment variables
        raw_url = (
            self.DATABASE_URL
            or self.POSTGRES_URL
            or self.POSTGRES_PRISMA_URL
            or self.POSTGRES_URL_NON_POOLING
            or os.environ.get("DATABASE_URL")
            or os.environ.get("POSTGRES_URL")
            or os.environ.get("POSTGRES_PRISMA_URL")
            or os.environ.get("POSTGRES_URL_NON_POOLING")
        )

        is_serverless = bool(
            os.environ.get("VERCEL")
            or os.environ.get("VERCEL_ENV")
            or os.environ.get("AWS_LAMBDA_FUNCTION_NAME")
        )

        if raw_url:
            return normalize_database_url(raw_url)

        # On Vercel / AWS Lambda, use SQLite in /tmp by default only if no managed DB is set
        if is_serverless:
            return "sqlite+aiosqlite:////tmp/repopilot.db"

        # Local development fallback
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # GitHub API
    GITHUB_TOKEN: Optional[str] = None

    # AI Configuration
    AI_PROVIDER: str = "openai"  # "openai" or "gemini"
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSION: int = 1536

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
