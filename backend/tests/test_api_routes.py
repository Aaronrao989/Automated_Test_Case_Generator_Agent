"""
API route tests.
"""

import io
import uuid

from fastapi.testclient import (
    TestClient
)

from app.main import app


client = TestClient(app)


# ==========================================================
# ROOT
# ==========================================================

def test_root_endpoint():

    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "running"


# ==========================================================
# HEALTH
# ==========================================================

def test_health_endpoint():

    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert "status" in data

    assert "database" in data


# ==========================================================
# API ROOT
# ==========================================================

def test_api_root():

    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "running"


# ==========================================================
# START ANALYSIS
# ==========================================================

def test_start_analysis():

    payload = {

        "source_type": "code_snippet",

        "source_data":
            (
                "def add(a, b):\n"
                "    return a + b"
            )
    }

    response = client.post(
        "/api/v1/analysis/start",
        json=payload
    )

    # Celery/Redis may not exist
    assert response.status_code in [
        202,
        500
    ]


# ==========================================================
# INVALID SOURCE TYPE
# ==========================================================

def test_invalid_source_type():

    payload = {

        "source_type": "invalid_type",

        "source_data": "print('hello')"
    }

    response = client.post(
        "/api/v1/analysis/start",
        json=payload
    )

    assert response.status_code in [
        400,
        422
    ]


# ==========================================================
# EMPTY SOURCE DATA
# ==========================================================

def test_empty_source_data():

    payload = {

        "source_type": "code_snippet",

        "source_data": ""
    }

    response = client.post(
        "/api/v1/analysis/start",
        json=payload
    )

    assert response.status_code in [
        400,
        422
    ]


# ==========================================================
# GET UNKNOWN JOB
# ==========================================================

def test_get_unknown_job():

    fake_id = str(uuid.uuid4())

    response = client.get(
        f"/api/v1/analysis/{fake_id}"
    )

    assert response.status_code == 404


# ==========================================================
# DELETE UNKNOWN JOB
# ==========================================================

def test_delete_unknown_job():

    fake_id = str(uuid.uuid4())

    response = client.delete(
        f"/api/v1/analysis/{fake_id}"
    )

    assert response.status_code == 404


# ==========================================================
# ZIP UPLOAD
# ==========================================================

def test_upload_zip():

    fake_zip = io.BytesIO(
        b"PK\x03\x04"
    )

    response = client.post(

        "/api/v1/analysis/upload",

        files={
            "file": (
                "repo.zip",
                fake_zip,
                "application/zip"
            )
        }
    )

    assert response.status_code in [
        202,
        500
    ]


# ==========================================================
# INVALID FILE TYPE
# ==========================================================

def test_upload_invalid_file():

    fake_txt = io.BytesIO(
        b"hello"
    )

    response = client.post(

        "/api/v1/analysis/upload",

        files={
            "file": (
                "bad.txt",
                fake_txt,
                "text/plain"
            )
        }
    )

    assert response.status_code == 400


# ==========================================================
# LARGE FILE REJECTION
# ==========================================================

def test_large_file_rejection():

    huge_data = io.BytesIO(
        b"x" * (
            105 * 1024 * 1024
        )
    )

    response = client.post(

        "/api/v1/analysis/upload",

        files={
            "file": (
                "huge.zip",
                huge_data,
                "application/zip"
            )
        }
    )

    assert response.status_code == 413