from sqlalchemy import (
    create_engine,
    text
)

from sqlalchemy.orm import (
    sessionmaker,
    declarative_base
)

from app.core.config import settings


# ==========================================================
# DATABASE URL
# ==========================================================

DATABASE_URL = settings.database_url


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

if DATABASE_URL.startswith("sqlite"):

    engine_kwargs.update({
        "connect_args": {
            "check_same_thread": False
        }
    })


# ==========================================================
# POSTGRESQL CONFIG
# ==========================================================

else:

    engine_kwargs.update({
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
        "pool_recycle": 3600
    })


# ==========================================================
# CREATE ENGINE
# ==========================================================

# Build connect_args based on database type
connect_args = {}

if DATABASE_URL.startswith("postgresql"):
    # PostgreSQL connection args
    connect_args = {
        "sslmode": "disable"  # Docker environment uses local network
    }

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args=connect_args,
    echo=False
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

    except Exception:

        return False