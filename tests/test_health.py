from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_check_status_code():
    """Verify that GET /health returns a 200 HTTP status code."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_check_response_body():
    """Verify that GET /health returns the expected status ok JSON payload."""
    response = client.get("/health")
    assert response.json() == {"status": "ok"}
