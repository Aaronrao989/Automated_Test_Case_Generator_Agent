"""Analysis routes (no authentication — public demo)."""

import logging
import os
import uuid
from pathlib import Path

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    Query,
    Request,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.rate_limit import analysis_rate_limiter
from app.db.database import get_db
from app.models import AnalysisJob, JobStatus
from app.schemas import AnalysisJobResponse, AnalysisStartRequest
from app.services.analysis_service import run_analysis

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analysis", tags=["analysis"])


def _validate_job_id(job_id: str) -> None:
    try:
        uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID")


def _safe_remove(path: str | None) -> None:
    try:
        if path and os.path.isfile(path):
            os.remove(path)
    except OSError:
        pass


@router.post("/start", response_model=AnalysisJobResponse, status_code=status.HTTP_202_ACCEPTED)
def start_analysis(
    payload: AnalysisStartRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
) -> AnalysisJobResponse:
    analysis_rate_limiter(request)

    job_id = str(uuid.uuid4())
    job = AnalysisJob(
        id=job_id,
        status=JobStatus.PENDING,
        source_type=payload.source_type,
        source_data=payload.source_data.strip(),
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    background_tasks.add_task(run_analysis, job_id, payload.source_type, payload.source_data.strip())
    return AnalysisJobResponse(job_id=job.id, status=job.status.value, created_at=job.created_at)


@router.post("/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_and_analyze(
    background_tasks: BackgroundTasks,
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    analysis_rate_limiter(request)

    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files are allowed")

    upload_dir = os.path.abspath(settings.upload_dir)
    os.makedirs(upload_dir, exist_ok=True)
    job_id = str(uuid.uuid4())
    _ = Path(file.filename).name  # strip any directory components
    saved_path = os.path.join(upload_dir, f"{job_id}.zip")

    total = 0
    try:
        with open(saved_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                total += len(chunk)
                if total > settings.max_file_size:
                    raise HTTPException(status_code=413, detail="File too large")
                buffer.write(chunk)
    except HTTPException:
        _safe_remove(saved_path)
        raise
    finally:
        await file.close()

    job = AnalysisJob(id=job_id, status=JobStatus.PENDING, source_type="zip_file", source_data=saved_path)
    db.add(job)
    db.commit()
    db.refresh(job)

    background_tasks.add_task(run_analysis, job_id, "zip_file", saved_path)
    return {"job_id": job.id, "status": job.status.value, "created_at": job.created_at.isoformat()}


@router.get("")
def list_analyses(db: Session = Depends(get_db), limit: int = Query(20, ge=1, le=50)):
    """Recent jobs (lightweight summary only — no heavy result payloads)."""
    jobs = db.query(AnalysisJob).order_by(AnalysisJob.created_at.desc()).limit(limit).all()
    return [
        {
            "job_id": job.id,
            "status": job.status.value,
            "source_type": job.source_type,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "stats": (job.results or {}).get("stats") if isinstance(job.results, dict) else None,
        }
        for job in jobs
    ]


@router.get("/{job_id}")
def get_analysis_result(job_id: str, db: Session = Depends(get_db)):
    _validate_job_id(job_id)
    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status in (JobStatus.PENDING, JobStatus.IN_PROGRESS):
        stage = (job.results or {}).get("stage") if isinstance(job.results, dict) else None
        return {"job_id": job.id, "status": job.status.value, "stage": stage or "queued"}

    if job.status == JobStatus.FAILED:
        return {"job_id": job.id, "status": job.status.value, "error": job.error_message or "Unknown error"}

    response = {
        "job_id": job.id,
        "status": job.status.value,
        "source_type": job.source_type,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "updated_at": job.updated_at.isoformat() if job.updated_at else None,
    }
    if isinstance(job.results, dict):
        response.update(job.results)
    return response


@router.delete("/{job_id}")
def delete_analysis_job(job_id: str, db: Session = Depends(get_db)):
    _validate_job_id(job_id)
    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.source_type == "zip_file" and job.source_data:
        _safe_remove(job.source_data)
    db.delete(job)
    db.commit()
    return {"message": "Job deleted", "job_id": job_id}
