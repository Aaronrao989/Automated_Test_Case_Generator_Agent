"""Background analysis worker (FastAPI BackgroundTasks)."""

import logging
import os

from app.agents.orchestrator import TestGenerationOrchestrator
from app.db.database import SessionLocal
from app.models import AnalysisJob, JobStatus

logger = logging.getLogger(__name__)


def run_analysis(job_id: str, source_type: str, source_data: str) -> None:
    """Execute a single analysis job and persist its result.

    Runs inside a FastAPI BackgroundTask (same process, no external worker).
    Progress is written to ``job.results['stage']`` so the frontend can poll it.
    """
    db = SessionLocal()
    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
    if job is None:
        db.close()
        return

    def report_stage(stage: str) -> None:
        job.results = {"stage": stage}
        db.commit()

    try:
        job.status = JobStatus.IN_PROGRESS
        report_stage("queued")

        orchestrator = TestGenerationOrchestrator(on_stage=report_stage)
        if source_type == "github_url":
            result = orchestrator.analyze_from_url(source_data)
        elif source_type == "zip_file":
            result = orchestrator.analyze_from_zip(source_data)
        else:
            result = orchestrator.analyze_from_text(source_data, "python")

        result["stage"] = "completed"
        job.status = JobStatus.COMPLETED
        job.results = result
        job.error_message = None
        db.commit()
        logger.info("Job %s completed", job_id)
    except Exception as exc:  # noqa: BLE001 - recorded on the job row
        logger.exception("Job %s failed", job_id)
        job.status = JobStatus.FAILED
        job.error_message = str(exc)
        job.results = None
        db.commit()
    finally:
        if source_type == "zip_file" and source_data and os.path.isfile(source_data):
            try:
                os.remove(source_data)
            except OSError:
                pass
        db.close()


def reconcile_stuck_jobs() -> int:
    """Mark jobs left mid-flight by a restart/spin-down as FAILED."""
    db = SessionLocal()
    try:
        stuck = (
            db.query(AnalysisJob)
            .filter(AnalysisJob.status.in_([JobStatus.PENDING, JobStatus.IN_PROGRESS]))
            .all()
        )
        for job in stuck:
            job.status = JobStatus.FAILED
            job.error_message = "Interrupted by a server restart. Please retry."
        db.commit()
        if stuck:
            logger.info("Reconciled %d stuck job(s) on startup", len(stuck))
        return len(stuck)
    finally:
        db.close()
