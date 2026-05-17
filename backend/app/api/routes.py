import os
import uuid
import traceback
from pathlib import Path

from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    UploadFile,
    File,
    status
)

from sqlalchemy.orm import Session

from app.db.database import (
    get_db,
    check_database_connection
)

from app.models import (
    AnalysisJob,
    JobStatus
)

from app.schemas import (
    AnalysisStartRequest,
    AnalysisJobResponse
)

from app.workers.tasks import (
    analyze_repository_task
)

from app.core.config import settings


router = APIRouter(
    prefix="/api/v1",
    tags=["analysis"]
)


# ==========================================================
# HELPERS
# ==========================================================

def normalize_source_type(
    source_type: str
) -> str:

    normalized = (
        source_type.strip().lower()
    )

    if normalized == "raw_code":

        normalized = "code_snippet"

    return normalized


def validate_job_id(
    job_id: str
):

    try:

        uuid.UUID(job_id)

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Invalid job ID"
        )


def safe_remove_file(
    file_path: str
):

    try:

        if (
            file_path
            and os.path.exists(file_path)
            and os.path.isfile(file_path)
        ):

            os.remove(file_path)

    except Exception:
        pass


# ==========================================================
# START ANALYSIS
# ==========================================================

@router.post(
    "/analysis/start",
    response_model=AnalysisJobResponse,
    status_code=status.HTTP_202_ACCEPTED
)
async def start_analysis(
    request: AnalysisStartRequest,
    db: Session = Depends(get_db)
):
    """
    Start repository/code analysis.
    """

    try:

        source_type = normalize_source_type(
            request.source_type
        )

        source_data = (
            request.source_data.strip()
        )

        # --------------------------------------------------
        # VALIDATION
        # --------------------------------------------------

        if not source_data:

            raise HTTPException(
                status_code=400,
                detail=(
                    "source_data cannot be empty"
                )
            )

        allowed_source_types = {
            "github_url",
            "zip_file",
            "user_story",
            "code_snippet"
        }

        if source_type not in allowed_source_types:

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Unsupported source type: "
                    f"{source_type}"
                )
            )

        # --------------------------------------------------
        # CREATE JOB
        # --------------------------------------------------

        job_id = str(uuid.uuid4())

        job = AnalysisJob(
            id=job_id,
            status=JobStatus.PENDING,
            source_type=source_type,
            source_data=source_data
        )

        db.add(job)

        db.commit()

        db.refresh(job)

        # --------------------------------------------------
        # RUN TASK DIRECTLY
        # --------------------------------------------------

        try:

            analyze_repository_task(
                job_id,
                source_type,
                source_data
            )

        except Exception as analysis_error:

            db.rollback()

            job.status = JobStatus.FAILED

            job.error_message = (
                f"Analysis error: "
                f"{str(analysis_error)}"
            )

            db.commit()

            raise HTTPException(
                status_code=500,
                detail="Analysis failed"
            )

        db.refresh(job)

        return AnalysisJobResponse(
            job_id=job.id,
            status=job.status.value,
            created_at=job.created_at
        )

    except HTTPException:
        raise

    except Exception as e:

        db.rollback()

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to start analysis: "
                f"{str(e)}"
            )
        )


# ==========================================================
# UPLOAD ZIP
# ==========================================================

@router.post(
    "/analysis/upload",
    status_code=status.HTTP_202_ACCEPTED
)
async def upload_and_analyze(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload ZIP repository and analyze.
    """

    saved_file_path = None

    try:

        # --------------------------------------------------
        # VALIDATE FILE
        # --------------------------------------------------

        if not file.filename:

            raise HTTPException(
                status_code=400,
                detail="No file uploaded"
            )

        filename = (
            Path(file.filename)
            .name
        )

        if not filename.lower().endswith(
            ".zip"
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "Only ZIP files are allowed"
                )
            )

        # --------------------------------------------------
        # CREATE DIRECTORY
        # --------------------------------------------------

        upload_dir = os.path.abspath(
            settings.upload_dir
        )

        os.makedirs(
            upload_dir,
            exist_ok=True
        )

        # --------------------------------------------------
        # CREATE FILE PATH
        # --------------------------------------------------

        job_id = str(uuid.uuid4())

        saved_file_path = os.path.join(
            upload_dir,
            f"{job_id}.zip"
        )

        # --------------------------------------------------
        # STREAM WRITE FILE
        # --------------------------------------------------

        total_size = 0

        with open(
            saved_file_path,
            "wb"
        ) as buffer:

            while True:

                chunk = await file.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                total_size += len(chunk)

                if (
                    total_size >
                    settings.max_file_size
                ):

                    buffer.close()

                    safe_remove_file(
                        saved_file_path
                    )

                    raise HTTPException(
                        status_code=413,
                        detail="File too large"
                    )

                buffer.write(chunk)

        # --------------------------------------------------
        # CREATE JOB
        # --------------------------------------------------

        job = AnalysisJob(
            id=job_id,
            status=JobStatus.PENDING,
            source_type="zip_file",
            source_data=saved_file_path
        )

        db.add(job)

        db.commit()

        db.refresh(job)

        # --------------------------------------------------
        # RUN TASK DIRECTLY
        # --------------------------------------------------

        try:

            analyze_repository_task(
                job_id,
                "zip_file",
                saved_file_path
            )

        except Exception as analysis_error:

            db.rollback()

            job.status = JobStatus.FAILED

            job.error_message = (
                f"Analysis error: "
                f"{str(analysis_error)}"
            )

            db.commit()

            raise HTTPException(
                status_code=500,
                detail=(
                    "ZIP analysis failed"
                )
            )

        db.refresh(job)

        return {
            "job_id": job.id,
            "status": job.status.value,
            "created_at": (
                job.created_at.isoformat()
            ),
            "message": (
                "ZIP uploaded and analyzed successfully"
            )
        }

    except HTTPException:
        raise

    except Exception as e:

        db.rollback()

        safe_remove_file(
            saved_file_path
        )

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )

    finally:

        await file.close()


# ==========================================================
# GET RESULT
# ==========================================================

@router.get("/analysis/{job_id}")
async def get_analysis_result(
    job_id: str,
    db: Session = Depends(get_db)
):
    """
    Fetch analysis result.
    """

    try:

        validate_job_id(job_id)

        job = (
            db.query(AnalysisJob)
            .filter(
                AnalysisJob.id == job_id
            )
            .first()
        )

        if not job:

            raise HTTPException(
                status_code=404,
                detail="Job not found"
            )

        # --------------------------------------------------
        # IN PROGRESS
        # --------------------------------------------------

        if job.status in [
            JobStatus.PENDING,
            JobStatus.IN_PROGRESS
        ]:

            return {
                "job_id": job.id,
                "status": job.status.value,
                "message": (
                    "Analysis in progress"
                )
            }

        # --------------------------------------------------
        # FAILED
        # --------------------------------------------------

        if job.status == JobStatus.FAILED:

            return {
                "job_id": job.id,
                "status": job.status.value,
                "error": (
                    job.error_message
                    or "Unknown error"
                )
            }

        # --------------------------------------------------
        # SUCCESS
        # --------------------------------------------------

        response = {
            "job_id": job.id,
            "status": job.status.value,
            "source_type": job.source_type,
            "created_at": (
                job.created_at.isoformat()
                if job.created_at
                else None
            ),
            "updated_at": (
                job.updated_at.isoformat()
                if job.updated_at
                else None
            )
        }

        if isinstance(
            job.results,
            dict
        ):

            response.update(
                job.results
            )

        return response

    except HTTPException:
        raise

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to fetch job: "
                f"{str(e)}"
            )
        )


# ==========================================================
# DELETE JOB
# ==========================================================

@router.delete("/analysis/{job_id}")
async def delete_analysis_job(
    job_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete analysis job.
    """

    try:

        validate_job_id(job_id)

        job = (
            db.query(AnalysisJob)
            .filter(
                AnalysisJob.id == job_id
            )
            .first()
        )

        if not job:

            raise HTTPException(
                status_code=404,
                detail="Job not found"
            )

        # --------------------------------------------------
        # DELETE ZIP FILE
        # --------------------------------------------------

        if (
            job.source_type == "zip_file"
            and job.source_data
        ):

            safe_remove_file(
                job.source_data
            )

        db.delete(job)

        db.commit()

        return {
            "message": (
                "Job deleted successfully"
            ),
            "job_id": job_id
        }

    except HTTPException:
        raise

    except Exception as e:

        db.rollback()

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=(
                "Delete failed: "
                f"{str(e)}"
            )
        )


# ==========================================================
# API HEALTH
# ==========================================================

@router.get("/health")
async def health_check():

    return {
        "status": "healthy",
        "service": (
            "Automated Test "
            "Case Generator API"
        ),
        "database": (
            "connected"
            if check_database_connection()
            else "disconnected"
        ),
        "llm_provider": (
            settings.llm_provider
        )
    }