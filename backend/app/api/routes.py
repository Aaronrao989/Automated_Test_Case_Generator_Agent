"""Aggregate API router mounted under /api/v1."""

from fastapi import APIRouter

from app.api import analysis

router = APIRouter(prefix="/api/v1")
router.include_router(analysis.router)
