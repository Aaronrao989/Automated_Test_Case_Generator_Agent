from pathlib import Path

from celery import Celery
from dotenv import load_dotenv

from app.core.config import settings


# ==========================================================
# LOAD ENV
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

ENV_FILE = BASE_DIR / ".env"

load_dotenv(
    dotenv_path=ENV_FILE,
    override=True
)


# ==========================================================
# CREATE CELERY APP
# ==========================================================

celery_app = Celery(
    "automated_test_generator",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend
)


# ==========================================================
# CELERY CONFIGURATION
# ==========================================================

celery_app.conf.update(

    # ------------------------------------------------------
    # SERIALIZATION
    # ------------------------------------------------------

    task_serializer="json",

    accept_content=["json"],

    result_serializer="json",

    # ------------------------------------------------------
    # TIMEZONE
    # ------------------------------------------------------

    timezone="UTC",

    enable_utc=True,

    # ------------------------------------------------------
    # TASK IMPORTS
    # ------------------------------------------------------

    imports=[
        "app.workers.tasks"
    ],

    # ------------------------------------------------------
    # RELIABILITY
    # ------------------------------------------------------

    broker_connection_retry_on_startup=True,

    task_track_started=True,

    task_acks_late=True,

    worker_prefetch_multiplier=1,

    # ------------------------------------------------------
    # MEMORY/STABILITY
    # ------------------------------------------------------

    worker_max_tasks_per_child=5,

    worker_max_memory_per_child=300000,

    # ------------------------------------------------------
    # TIME LIMITS
    # ------------------------------------------------------

    task_soft_time_limit=300,

    task_time_limit=360,

    # ------------------------------------------------------
    # RESULT BACKEND
    # ------------------------------------------------------

    result_expires=3600,

    result_extended=True,

    # ------------------------------------------------------
    # TASK ROUTING
    # ------------------------------------------------------

    task_default_queue="default",

    task_default_exchange="default",

    task_default_routing_key="default",

    # ------------------------------------------------------
    # WORKER SETTINGS
    # ------------------------------------------------------

    worker_send_task_events=False,

    task_send_sent_event=False,

    # ------------------------------------------------------
    # SECURITY
    # ------------------------------------------------------

    worker_hijack_root_logger=False,
)


# ==========================================================
# OPTIONAL DEBUG
# ==========================================================

if settings.llm_provider == "groq":

    print(
        "[Celery] Running with Groq provider"
    )

print(
    f"[Celery] Broker: "
    f"{settings.celery_broker_url}"
)