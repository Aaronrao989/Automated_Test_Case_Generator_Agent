import traceback

from app.db.database import SessionLocal

from app.models import (
    AnalysisJob,
    JobStatus
)

from app.agents.orchestrator import (
    TestGenerationOrchestrator
)


def run_analysis(
    job_id: str,
    source_type: str,
    source_data: str
):

    db = SessionLocal()

    job = None

    try:

        job = (
            db.query(AnalysisJob)
            .filter(
                AnalysisJob.id == job_id
            )
            .first()
        )

        if not job:
            return

        # ==========================================
        # UPDATE STATUS
        # ==========================================

        job.status = JobStatus.IN_PROGRESS

        db.commit()

        # ==========================================
        # ORCHESTRATOR
        # ==========================================

        orchestrator = (
            TestGenerationOrchestrator()
        )

        # ==========================================
        # ANALYSIS
        # ==========================================

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

        # ==========================================
        # SAVE RESULTS
        # ==========================================

        job.status = JobStatus.COMPLETED

        job.results = result

        job.error_message = None

        db.commit()

    except Exception as e:

        traceback.print_exc()

        if job:

            job.status = JobStatus.FAILED

            job.error_message = str(e)

            db.commit()

    finally:

        db.close()