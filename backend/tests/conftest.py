"""Shared pytest fixtures.

Environment variables are set *before* the app is imported so cached settings
pick up the test configuration (SQLite DB, offline LLM mode).
"""

import os
import tempfile

_TEST_DB = os.path.join(tempfile.gettempdir(), "atcg_test.db")
os.environ.update(
    DATABASE_URL=f"sqlite:///{_TEST_DB}",
    GROQ_API_KEY="",  # offline demo mode — no network calls
    LLM_PROVIDER="groq",
    ENVIRONMENT="development",
    CORS_ORIGINS="http://localhost:3000",
)

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.db.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402

Base.metadata.create_all(bind=engine)


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session", autouse=True)
def _cleanup():
    yield
    try:
        os.remove(_TEST_DB)
    except OSError:
        pass
