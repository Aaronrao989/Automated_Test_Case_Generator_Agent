"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.core.config import settings
from app.db.database import Base, check_database_connection, engine
from app.services.analysis_service import reconcile_stuck_jobs

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting API (provider=%s model=%s)", settings.llm_provider, settings.groq_model)
    Base.metadata.create_all(bind=engine)
    reconcile_stuck_jobs()
    yield
    logger.info("API shutting down")


app = FastAPI(
    title="Automated Test Case Generator Agent",
    description="AI-powered automated test generation platform",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    # Also accept any Vercel domain (production + preview deployments) so the
    # public demo works without hand-matching exact origins.
    allow_origin_regex=r"https://([a-z0-9-]+\.)*vercel\.app",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Log the detail server-side; never leak internals to the client.
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health", tags=["health"])
def health_check():
    connected = check_database_connection()
    return {
        "status": "healthy" if connected else "degraded",
        "database": "connected" if connected else "disconnected",
        "llm_provider": settings.llm_provider,
    }


@app.get("/", tags=["health"])
def read_root():
    return {"message": "Automated Test Case Generator API", "version": "2.0.0"}
