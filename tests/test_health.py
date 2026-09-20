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


def test_readiness_probe():
    """Verify that GET /health/ready returns 200 and indicates reachable DB."""
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json().get("status") == "ready"


def test_root_metadata():
    """Verify that GET / returns service metadata."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert data["status"] == "online"
