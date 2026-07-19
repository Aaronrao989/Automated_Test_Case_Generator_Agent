"""API-level tests (no auth; end-to-end snippet analysis)."""

import time


def _wait(client, job_id, timeout=20):
    result = None
    for _ in range(timeout * 5):
        result = client.get(f"/api/v1/analysis/{job_id}").json()
        if result.get("status") in {"COMPLETED", "FAILED"}:
            break
        time.sleep(0.2)
    return result


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] in {"healthy", "degraded"}


def test_start_and_complete(client):
    code = "def add(a, b):\n    return a + b\n"
    resp = client.post(
        "/api/v1/analysis/start",
        json={"source_type": "code_snippet", "source_data": code},
    )
    assert resp.status_code == 202
    job_id = resp.json()["job_id"]

    result = _wait(client, job_id)
    assert result["status"] == "COMPLETED"
    assert result["structure"]["functions"][0]["name"] == "add"
    assert result["stats"]["functions_analyzed"] == 1
    assert "test_cases" in result["stats"]


def test_list_recent(client):
    # ensure at least one job exists
    client.post(
        "/api/v1/analysis/start",
        json={"source_type": "code_snippet", "source_data": "def f():\n    return 1\n"},
    )
    resp = client.get("/api/v1/analysis?limit=5")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert "job_id" in data[0]


def test_invalid_source_type_rejected(client):
    resp = client.post(
        "/api/v1/analysis/start",
        json={"source_type": "bogus", "source_data": "x"},
    )
    assert resp.status_code == 422


def test_get_invalid_job_id(client):
    assert client.get("/api/v1/analysis/not-a-uuid").status_code == 400


def test_delete_job(client):
    resp = client.post(
        "/api/v1/analysis/start",
        json={"source_type": "code_snippet", "source_data": "def g():\n    return 2\n"},
    )
    job_id = resp.json()["job_id"]
    _wait(client, job_id)
    assert client.delete(f"/api/v1/analysis/{job_id}").status_code == 200
    assert client.get(f"/api/v1/analysis/{job_id}").status_code == 404
