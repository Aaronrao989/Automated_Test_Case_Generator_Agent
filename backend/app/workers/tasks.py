import logging
from pathlib import Path

from celery import Task
from dotenv import load_dotenv

from app.agents.orchestrator import (
    TestGenerationOrchestrator
)

from app.core.config import settings

from app.db.database import (
    SessionLocal
)

from app.models import (
    AnalysisJob,
    JobStatus
)

from app.workers.celery_app import (
    celery_app
)


# ==========================================================
# LOAD ENV
# ==========================================================

env_path = (
    Path(__file__).parent.parent.parent
    / ".env"
)

if env_path.exists():

    load_dotenv(
        dotenv_path=env_path,
        override=True
    )


# ==========================================================
# LOGGER
# ==========================================================

logger = logging.getLogger(__name__)


# ==========================================================
# BASE TASK
# ==========================================================

class CallbackTask(Task):
    """
    Shared Celery task behavior.
    """

    autoretry_for = (
        ConnectionError,
        TimeoutError,
    )

    retry_kwargs = {
        "max_retries": 2
    }

    retry_backoff = True

    retry_backoff_max = 30

    retry_jitter = True

    def on_failure(
        self,
        exc,
        task_id,
        args,
        kwargs,
        einfo
    ):

        logger.error(
            f"[Celery] Task failed: {task_id}"
        )

        logger.error(str(exc))

        logger.error(str(einfo))


# ==========================================================
# MAIN ANALYSIS TASK
# ==========================================================

@celery_app.task(
    bind=True,
    base=CallbackTask,
    name="analyze_repository_task"
)
def analyze_repository_task(
    self,
    job_id: str,
    source_type: str,
    source_data: str
):

    db = SessionLocal()

    job = None

    try:

        logger.info(
            f"[Job {job_id}] Task started"
        )

        # ==================================================
        # INPUT VALIDATION
        # ==================================================

        if not source_data:

            raise ValueError(
                "source_data cannot be empty"
            )

        if len(source_data) > 2_000_000:

            raise ValueError(
                "source_data exceeds allowed size"
            )

        source_type = (
            source_type
            .strip()
            .lower()
        )

        valid_source_types = {
            "github_url",
            "zip_file",
            "user_story",
            "raw_code",
            "code_snippet"
        }

        if source_type not in valid_source_types:

            raise ValueError(
                f"Unsupported source_type: "
                f"{source_type}"
            )

        if source_type == "raw_code":

            source_type = "code_snippet"

        # ==================================================
        # FETCH JOB
        # ==================================================

        job = (
            db.query(AnalysisJob)
            .filter(
                AnalysisJob.id == job_id
            )
            .first()
        )

        if not job:

            raise ValueError(
                f"Job not found: {job_id}"
            )

        # ==================================================
        # UPDATE STATUS
        # ==================================================

        job.status = JobStatus.IN_PROGRESS

        db.commit()

        # ==================================================
        # DEBUG INFO
        # ==================================================

        logger.info(
            f"[Job {job_id}] "
            f"Source type: {source_type}"
        )

        logger.info(
            f"[Job {job_id}] "
            f"LLM Provider: "
            f"{settings.llm_provider}"
        )

        logger.info(
            f"[Job {job_id}] "
            f"Groq Model: "
            f"{settings.groq_model}"
        )

        # ==================================================
        # ORCHESTRATOR
        # ==================================================

        orchestrator = (
            TestGenerationOrchestrator()
        )

        # ==================================================
        # ROUTING
        # ==================================================

        if source_type == "github_url":

            result = (
                orchestrator.analyze_from_url(
                    source_data
                )
            )

        elif source_type == "zip_file":

            result = (
                orchestrator.analyze_from_zip(
                    source_data
                )
            )

        else:

            result = (
                orchestrator.analyze_from_text(
                    source_data,
                    "python"
                )
            )

        # ==================================================
        # VALIDATE RESULT
        # ==================================================

        if not isinstance(result, dict):

            raise ValueError(
                "Analysis result must be dictionary"
            )

        # ==================================================
        # REDUCE STORED PAYLOAD
        # ==================================================

        trimmed_result = {
            "job_id": result.get("job_id"),
            "status": result.get("status"),
            "structure": result.get("structure"),
            "coverage": result.get("coverage"),
            "tests": result.get("tests", []),
            "edge_cases": result.get(
                "edge_cases",
                []
            ),
            "saved_test_files": result.get(
                "saved_test_files",
                []
            ),
            "llm_provider": result.get(
                "llm_provider"
            ),
            "summary": {
                "tests_generated": len(
                    result.get("tests", [])
                ),
                "edge_cases_found": len(
                    result.get("edge_cases", [])
                ),
                "test_results": len(
                    result.get(
                        "test_results",
                        []
                    )
                )
            }
        }

        # ==================================================
        # SAVE RESULTS
        # ==================================================

        job.status = JobStatus.COMPLETED

        job.results = trimmed_result

        job.error_message = None

        db.commit()

        logger.info(
            f"[Job {job_id}] "
            f"Analysis completed"
        )

        return trimmed_result

    except Exception as e:

        db.rollback()

        error_message = str(e)

        logger.error(
            f"[Job {job_id}] Analysis failed"
        )

        logger.exception(e)

        try:

            if job:

                job.status = JobStatus.FAILED

                job.error_message = error_message

                db.commit()

        except Exception as db_error:

            logger.error(
                f"[Job {job_id}] "
                f"DB update failed: "
                f"{db_error}"
            )

        return {
            "job_id": job_id,
            "status": "FAILED",
            "error": error_message
        }

    finally:

        db.close()

        logger.info(
            f"[Job {job_id}] "
            f"DB session closed"
        )