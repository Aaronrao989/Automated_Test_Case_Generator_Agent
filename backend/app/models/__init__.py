from datetime import datetime
import enum

from sqlalchemy import (
    Column,
    String,
    Integer,
    Text,
    DateTime,
    Float,
    JSON,
    Enum
)

# IMPORTANT:
# Import shared Base from database.py
from app.db.database import Base


# ==========================================================
# JOB STATUS ENUM
# ==========================================================

class JobStatus(str, enum.Enum):

    PENDING = "PENDING"

    IN_PROGRESS = "IN_PROGRESS"

    COMPLETED = "COMPLETED"

    FAILED = "FAILED"


# ==========================================================
# ANALYSIS JOB
# ==========================================================

class AnalysisJob(Base):

    __tablename__ = "analysis_jobs"

    id = Column(
        String,
        primary_key=True,
        index=True
    )

    status = Column(
        Enum(JobStatus),
        nullable=False,
        default=JobStatus.PENDING
    )

    source_type = Column(
        String,
        nullable=False
    )

    source_data = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    error_message = Column(
        Text,
        nullable=True
    )

    results = Column(
        JSON,
        nullable=True
    )


# ==========================================================
# REPOSITORY STRUCTURE
# ==========================================================

class RepoStructure(Base):

    __tablename__ = "repo_structures"

    id = Column(
        String,
        primary_key=True,
        index=True
    )

    job_id = Column(
        String,
        nullable=False,
        index=True
    )

    languages = Column(
        JSON,
        nullable=True
    )

    files = Column(
        JSON,
        nullable=True
    )

    functions = Column(
        JSON,
        nullable=True
    )

    dependencies = Column(
        JSON,
        nullable=True
    )


# ==========================================================
# GENERATED TESTS
# ==========================================================

class GeneratedTest(Base):

    __tablename__ = "generated_tests"

    id = Column(
        String,
        primary_key=True,
        index=True
    )

    job_id = Column(
        String,
        nullable=False,
        index=True
    )

    test_type = Column(
        String,
        nullable=False
    )

    file_path = Column(
        String,
        nullable=False
    )

    content = Column(
        Text,
        nullable=False
    )

    language = Column(
        String,
        nullable=False
    )

    target_function = Column(
        String,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )


# ==========================================================
# TEST EXECUTION RESULTS
# ==========================================================

class TestExecutionResult(Base):

    __tablename__ = "test_execution_results"

    id = Column(
        String,
        primary_key=True,
        index=True
    )

    job_id = Column(
        String,
        nullable=False,
        index=True
    )

    test_id = Column(
        String,
        nullable=False
    )

    status = Column(
        String,
        nullable=False
    )

    duration = Column(
        Float,
        nullable=False,
        default=0.0
    )

    output = Column(
        Text,
        nullable=True
    )

    error = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )


# ==========================================================
# COVERAGE REPORT
# ==========================================================

class CoverageReport(Base):

    __tablename__ = "coverage_reports"

    id = Column(
        String,
        primary_key=True,
        index=True
    )

    job_id = Column(
        String,
        nullable=False,
        index=True
    )

    total_coverage = Column(
        Float,
        nullable=False,
        default=0.0
    )

    covered_lines = Column(
        Integer,
        nullable=False,
        default=0
    )

    total_lines = Column(
        Integer,
        nullable=False,
        default=0
    )

    file_coverage = Column(
        JSON,
        nullable=True
    )

    uncovered_code = Column(
        JSON,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )


# ==========================================================
# EDGE CASES
# ==========================================================

class EdgeCase(Base):

    __tablename__ = "edge_cases"

    id = Column(
        String,
        primary_key=True,
        index=True
    )

    job_id = Column(
        String,
        nullable=False,
        index=True
    )

    function_name = Column(
        String,
        nullable=False
    )

    edge_case_type = Column(
        String,
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    suggested_test = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )