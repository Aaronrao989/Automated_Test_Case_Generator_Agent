"""Database models.

The application stores the full analysis output as a JSON document on the
single ``AnalysisJob`` row. This keeps the schema trivial to operate on a
free Postgres tier while remaining easy to query by job id.
"""

import enum
from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, Enum, String, Text

from app.db.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"

    id = Column(String, primary_key=True, index=True)
    status = Column(
        Enum(JobStatus), nullable=False, default=JobStatus.PENDING, index=True
    )
    source_type = Column(String, nullable=False)
    # For uploads this is a temporary path; for snippets, the code itself.
    source_data = Column(Text, nullable=False)
    error_message = Column(Text, nullable=True)
    results = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=_utcnow,
        onupdate=_utcnow,
        nullable=False,
    )
