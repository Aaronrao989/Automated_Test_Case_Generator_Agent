from sqlalchemy import (
    create_engine,
    text
)

from sqlalchemy.orm import (
    sessionmaker,
    declarative_base
)

import os


# ==========================================================
# DATABASE URL
# ==========================================================

# Priority:
# 1. Environment variable
# 2. SQLite fallback for local tests

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./test.db"
)


# ==========================================================
# BASE MODEL
# ==========================================================

# IMPORTANT:
# This is the SINGLE shared Base
# used across the entire application.

Base = declarative_base()


# ==========================================================
# ENGINE CONFIGURATION
# ==========================================================

engine_kwargs = {
    "echo": False,
    "future": True
}


# ==========================================================
# SQLITE CONFIG
# ==========================================================

connect_args = {}

if DATABASE_URL.startswith("sqlite"):

    connect_args = {
        "check_same_thread": False
    }

    engine_kwargs.update({
        "connect_args": connect_args
    })


# ==========================================================
# SUPABASE / POSTGRES CONFIG
# ==========================================================

elif "supabase.com" in DATABASE_URL:

    connect_args = {
        "sslmode": "require"
    }

    engine_kwargs.update({
        "connect_args": connect_args,
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
        "pool_recycle": 3600
    })


# ==========================================================
# LOCAL POSTGRES / DOCKER CONFIG
# ==========================================================

elif DATABASE_URL.startswith("postgresql"):

    engine_kwargs.update({
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
        "pool_recycle": 3600
    })


# ==========================================================
# CREATE ENGINE
# ==========================================================

engine = create_engine(
    DATABASE_URL,
    **engine_kwargs
)


# ==========================================================
# SESSION FACTORY
# ==========================================================

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)


# ==========================================================
# DATABASE DEPENDENCY
# ==========================================================

def get_db():
    """
    FastAPI database dependency.
    """

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()


# ==========================================================
# DATABASE HEALTH CHECK
# ==========================================================

def check_database_connection() -> bool:
    """
    Verify database connectivity.
    """

    try:

        with engine.connect() as connection:

            connection.execute(
                text("SELECT 1")
            )

        return True

    except Exception as e:

        print(f"Database connection failed: {e}")

        return False