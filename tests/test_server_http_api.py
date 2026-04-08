from pathlib import Path
import sys

from fastapi.testclient import TestClient


sys.path.append(str(Path(__file__).resolve().parents[1]))

from server.app import app


client = TestClient(app)


def test_metadata_includes_tasks_and_graders():
    response = client.get("/metadata")

    assert response.status_code == 200
    payload = response.json()

    assert payload["name"] == "InboxEnvironment"
    assert len(payload["tasks"]) == 3
    assert payload["tasks"][0]["id"] == "task_1"
    assert payload["tasks"][0]["graders"][0]["name"] == "priority"


def test_tasks_endpoint_returns_catalog():
    response = client.get("/tasks")

    assert response.status_code == 200
    payload = response.json()

    assert len(payload["tasks"]) == 3
    assert payload["tasks"][2]["id"] == "task_3"
    assert any(grader["name"] == "response_quality" for grader in payload["tasks"][2]["graders"])


def test_health_endpoint_matches_expected_contract():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
