import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.db.database import (
    Base,
    engine
)

from app.api.routes import router
from app.core.config import settings


# ==========================================================
# LOGGING CONFIG
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    )
)

logger = logging.getLogger(__name__)


# ==========================================================
# DATABASE INITIALIZATION
# ==========================================================

def initialize_database() -> None:
    """
    Initialize database tables.
    """

    try:

        Base.metadata.create_all(bind=engine)

        logger.info(
            "[Startup] Database tables created successfully"
        )

    except Exception:

        logger.exception(
            "[Startup] Database initialization failed"
        )

        logger.warning(
            "Application will continue without DB initialization"
        )


# ==========================================================
# DATABASE HEALTH CHECK
# ==========================================================

def check_database_connection() -> bool:
    """
    Check database connectivity.
    """

    try:

        with engine.connect() as connection:

            connection.execute(
                text("SELECT 1")
            )

        return True

    except Exception as e:

        logger.warning(
            f"[Health] Database connection failed: {e}"
        )

        return False


# ==========================================================
# APPLICATION LIFESPAN
# ==========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info(
        "[Startup] Automated Test Generator API starting"
    )

    logger.info(
        f"[Startup] LLM Provider: "
        f"{settings.llm_provider}"
    )

    logger.info(
        f"[Startup] Groq Model: "
        f"{settings.groq_model}"
    )

    initialize_database()

    yield

    logger.info(
        "[Shutdown] API shutting down"
    )


# ==========================================================
# CREATE FASTAPI APP
# ==========================================================

app = FastAPI(
    title="Automated Test Case Generator Agent",
    description=(
        "AI-powered automated test generation platform"
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)


# ==========================================================
# CORS CONFIG
# ==========================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[

        # LOCALHOST

        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",

        # LOCAL NETWORK

        "http://192.168.1.17:3002",

        # RENDER BACKEND

        "https://automated-test-case-generator-agent.onrender.com",

        # VERCEL FRONTEND

        "https://automatedtestcasegeneratoragent.vercel.app",
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ==========================================================
# ROUTES
# ==========================================================

app.include_router(router)


# ==========================================================
# ROOT ENDPOINT
# ==========================================================

@app.get("/")
async def read_root():

    return {
        "message": (
            "Welcome to the Automated Test Case Generator API"
        ),

        "status": "running",

        "version": "1.0.0",

        "llm_provider": settings.llm_provider
    }


# ==========================================================
# APPLICATION INFO
# ==========================================================

@app.get("/info")
async def app_info():

    return {
        "application": (
            "Automated Test Case Generator Agent"
        ),

        "features": [
            "Repository scanning",
            "AI-generated tests",
            "Edge case analysis",
            "Pytest execution",
            "Coverage analysis",
            "Groq LLM integration"
        ],

        "supported_languages": [
            "Python",
            "JavaScript",
            "TypeScript"
        ],

        "llm_provider": settings.llm_provider,

        "model": settings.groq_model
    }


# ==========================================================
# HEALTH CHECK
# ==========================================================

@app.get("/health")
async def health_check():

    db_connected = check_database_connection()

    return {
        "status": (
            "healthy"
            if db_connected
            else "degraded"
        ),

        "api": "running",

        "database": (
            "connected"
            if db_connected
            else "disconnected"
        ),

        "llm_provider": settings.llm_provider,

        "model": settings.groq_model
    }