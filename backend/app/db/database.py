"""Database engine, session factory, and helpers."""

import logging

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()


def _build_engine():
    """Create an engine with sensible, free-tier-friendly pooling."""
    url = settings.database_url
    kwargs: dict = {"future": True, "echo": False}

    if url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    else:
        # Small pool: free Postgres tiers (Render/Supabase) cap connections.
        kwargs.update(
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=5,
            pool_recycle=1800,
        )
        if "supabase.co" in url or "supabase.com" in url:
            kwargs.setdefault("connect_args", {})["sslmode"] = "require"

    return create_engine(url, **kwargs)


engine = _build_engine()

SessionLocal = sessionmaker(
    bind=engine, autocommit=False, autoflush=False, expire_on_commit=False
)


def get_db():
    """FastAPI dependency yielding a scoped session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> bool:
    """Return True if the database is reachable."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception as exc:  # noqa: BLE001 - surfaced via health endpoint
        logger.warning("Database connection failed: %s", exc)
        return False
