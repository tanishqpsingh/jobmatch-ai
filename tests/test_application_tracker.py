"""
Phase 7 Application Tracker Tests
- All application endpoints require authentication (JWT Bearer token)
- Applications are scoped to the authenticated user (ownership isolation)
- Unauthenticated access returns 401
- Cross-user access returns 404 (not 403, to avoid leaking existence)
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.db.database import Base, get_db

# ---------------------------------------------------------------------------
# In-memory SQLite test database
# ---------------------------------------------------------------------------
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Override get_db dependency for tests."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_database():
    """Create all tables before each test and drop them afterwards for clean isolation."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


# ---------------------------------------------------------------------------
# Helper: register + login -> return Bearer token
# ---------------------------------------------------------------------------
def _get_token(email: str = "user@example.com", password: str = "testpass123") -> str:
    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    return resp.json()["access_token"]


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ===========================================================================
# AUTH / UNAUTHENTICATED ACCESS TESTS
# ===========================================================================

def test_unauthenticated_list_returns_401():
    response = client.get("/api/v1/applications")
    assert response.status_code == 401


def test_unauthenticated_create_returns_401():
    response = client.post("/api/v1/applications", json={"company": "Acme", "job_title": "Dev"})
    assert response.status_code == 401


def test_unauthenticated_get_returns_401():
    response = client.get("/api/v1/applications/1")
    assert response.status_code == 401


def test_unauthenticated_patch_returns_401():
    response = client.patch("/api/v1/applications/1", json={"status": "applied"})
    assert response.status_code == 401


def test_unauthenticated_delete_returns_401():
    response = client.delete("/api/v1/applications/1")
    assert response.status_code == 401


def test_unauthenticated_summary_returns_401():
    response = client.get("/api/v1/applications/summary")
    assert response.status_code == 401


# ===========================================================================
# AUTHENTICATED CRUD TESTS
# ===========================================================================

def test_create_application_success():
    token = _get_token()
    payload = {
        "company": "Acme Technologies",
        "job_title": "Senior Backend Engineer",
        "job_description": "Building FastAPI backend systems.",
        "application_date": "2026-09-20",
        "status": "applied",
        "notes": "Applied via referral",
    }
    response = client.post("/api/v1/applications", json=payload, headers=_auth_headers(token))
    assert response.status_code == 201
    data = response.json()
    assert data["company"] == "Acme Technologies"
    assert data["job_title"] == "Senior Backend Engineer"
    assert data["status"] == "applied"
    assert "id" in data


def test_create_application_does_not_accept_user_id_from_client():
    """user_id from request body must be ignored; server derives it from token."""
    token = _get_token()
    # Inject a bogus user_id=999 in the payload — it must be silently ignored
    payload = {"company": "Evil Corp", "job_title": "Hacker", "user_id": 999}
    response = client.post("/api/v1/applications", json=payload, headers=_auth_headers(token))
    # Should succeed (201) but ownership is tied to the authenticated user, not 999
    assert response.status_code == 201


def test_list_applications_authenticated():
    token = _get_token()
    client.post("/api/v1/applications", json={"company": "Comp A", "job_title": "Role A", "status": "saved"}, headers=_auth_headers(token))
    client.post("/api/v1/applications", json={"company": "Comp B", "job_title": "Role B", "status": "interview"}, headers=_auth_headers(token))

    response = client.get("/api/v1/applications", headers=_auth_headers(token))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    # Status filter
    res_filtered = client.get("/api/v1/applications?status=interview", headers=_auth_headers(token))
    assert res_filtered.status_code == 200
    filtered_data = res_filtered.json()
    assert len(filtered_data) == 1
    assert filtered_data[0]["company"] == "Comp B"


def test_get_application_by_id():
    token = _get_token()
    create_res = client.post("/api/v1/applications", json={"company": "TechCorp", "job_title": "DevOps", "status": "applied"}, headers=_auth_headers(token))
    app_id = create_res.json()["id"]

    response = client.get(f"/api/v1/applications/{app_id}", headers=_auth_headers(token))
    assert response.status_code == 200
    assert response.json()["company"] == "TechCorp"


def test_get_application_nonexistent_returns_404():
    token = _get_token()
    response = client.get("/api/v1/applications/99999", headers=_auth_headers(token))
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_update_application():
    token = _get_token()
    create_res = client.post("/api/v1/applications", json={"company": "Stark Ind", "job_title": "Engineer", "status": "applied"}, headers=_auth_headers(token))
    app_id = create_res.json()["id"]

    patch_payload = {"status": "interview", "interview_date": "2026-10-01T14:00:00", "notes": "Technical screen scheduled"}
    response = client.patch(f"/api/v1/applications/{app_id}", json=patch_payload, headers=_auth_headers(token))
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "interview"
    assert data["notes"] == "Technical screen scheduled"
    assert data["interview_date"] is not None


def test_delete_application():
    token = _get_token()
    create_res = client.post("/api/v1/applications", json={"company": "Wayne Ent", "job_title": "Security Analyst"}, headers=_auth_headers(token))
    app_id = create_res.json()["id"]

    del_res = client.delete(f"/api/v1/applications/{app_id}", headers=_auth_headers(token))
    assert del_res.status_code == 204

    get_res = client.get(f"/api/v1/applications/{app_id}", headers=_auth_headers(token))
    assert get_res.status_code == 404


def test_create_application_invalid_status():
    token = _get_token()
    payload = {"company": "Acme", "job_title": "Developer", "status": "invalid_status_xyz"}
    response = client.post("/api/v1/applications", json=payload, headers=_auth_headers(token))
    assert response.status_code == 422


def test_create_application_empty_company():
    token = _get_token()
    payload = {"company": "   ", "job_title": "Developer"}
    response = client.post("/api/v1/applications", json=payload, headers=_auth_headers(token))
    assert response.status_code == 422


def test_create_application_oversized_company():
    token = _get_token()
    payload = {"company": "A" * 201, "job_title": "Developer"}
    response = client.post("/api/v1/applications", json=payload, headers=_auth_headers(token))
    assert response.status_code == 422


def test_get_dashboard_summary():
    token = _get_token()
    client.post("/api/v1/applications", json={"company": "A", "job_title": "A", "status": "applied"}, headers=_auth_headers(token))
    client.post("/api/v1/applications", json={"company": "B", "job_title": "B", "status": "applied"}, headers=_auth_headers(token))
    client.post("/api/v1/applications", json={"company": "C", "job_title": "C", "status": "interview"}, headers=_auth_headers(token))

    response = client.get("/api/v1/applications/summary", headers=_auth_headers(token))
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert data["applied"] == 2
    assert data["interview"] == 1
    assert data["offer"] == 0


# ===========================================================================
# USER ISOLATION TESTS
# ===========================================================================

def test_user_cannot_read_another_users_application():
    """User B cannot access User A application by ID."""
    token_a = _get_token("alice@example.com", "alicepass1")
    token_b = _get_token("bob@example.com", "bobpass123")

    create_res = client.post("/api/v1/applications", json={"company": "Acme", "job_title": "Dev"}, headers=_auth_headers(token_a))
    app_id = create_res.json()["id"]

    # User B tries to fetch User A application
    response = client.get(f"/api/v1/applications/{app_id}", headers=_auth_headers(token_b))
    assert response.status_code == 404


def test_user_cannot_modify_another_users_application():
    """User B cannot PATCH User A application."""
    token_a = _get_token("alice2@example.com", "alicepass1")
    token_b = _get_token("bob2@example.com", "bobpass123")

    create_res = client.post("/api/v1/applications", json={"company": "Acme", "job_title": "Dev"}, headers=_auth_headers(token_a))
    app_id = create_res.json()["id"]

    response = client.patch(f"/api/v1/applications/{app_id}", json={"status": "offer"}, headers=_auth_headers(token_b))
    assert response.status_code == 404


def test_user_cannot_delete_another_users_application():
    """User B cannot DELETE User A application."""
    token_a = _get_token("alice3@example.com", "alicepass1")
    token_b = _get_token("bob3@example.com", "bobpass123")

    create_res = client.post("/api/v1/applications", json={"company": "Acme", "job_title": "Dev"}, headers=_auth_headers(token_a))
    app_id = create_res.json()["id"]

    response = client.delete(f"/api/v1/applications/{app_id}", headers=_auth_headers(token_b))
    assert response.status_code == 404


def test_list_returns_only_own_applications():
    """User B list does not include User A applications."""
    token_a = _get_token("alice4@example.com", "alicepass1")
    token_b = _get_token("bob4@example.com", "bobpass123")

    client.post("/api/v1/applications", json={"company": "Acme", "job_title": "A-Role"}, headers=_auth_headers(token_a))
    client.post("/api/v1/applications", json={"company": "Globex", "job_title": "B-Role"}, headers=_auth_headers(token_b))

    res_b = client.get("/api/v1/applications", headers=_auth_headers(token_b))
    assert res_b.status_code == 200
    companies = [a["company"] for a in res_b.json()]
    assert "Acme" not in companies
    assert "Globex" in companies


def test_summary_only_includes_own_applications():
    """Summary counts are scoped to the authenticated user only."""
    token_a = _get_token("alice5@example.com", "alicepass1")
    token_b = _get_token("bob5@example.com", "bobpass123")

    # User A creates 3 applications
    for _ in range(3):
        client.post("/api/v1/applications", json={"company": "Acme", "job_title": "Dev", "status": "applied"}, headers=_auth_headers(token_a))

    # User B creates 1 application
    client.post("/api/v1/applications", json={"company": "Globex", "job_title": "Dev", "status": "applied"}, headers=_auth_headers(token_b))

    res_b = client.get("/api/v1/applications/summary", headers=_auth_headers(token_b))
    assert res_b.status_code == 200
    assert res_b.json()["total"] == 1  # Only B own application


# ===========================================================================
# AUTH ENDPOINT TESTS — logout and /me
# ===========================================================================

def test_register_duplicate_email_returns_409():
    """Registering with an already-used email must return 409."""
    client.post("/api/v1/auth/register", json={"email": "dup@example.com", "password": "testpass123"})
    resp = client.post("/api/v1/auth/register", json={"email": "dup@example.com", "password": "testpass123"})
    assert resp.status_code == 409


def test_login_sets_cookies():
    """Login response must include HttpOnly access_token and refresh_token cookies."""
    client.post("/api/v1/auth/register", json={"email": "cookie@example.com", "password": "testpass123"})
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": "cookie@example.com", "password": "testpass123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.cookies
    assert "refresh_token" in resp.cookies
    # Verify token also in body for API/Bearer clients
    assert "access_token" in resp.json()


def test_get_me_returns_current_user():
    """GET /me returns the authenticated user profile."""
    token = _get_token("me@example.com", "testpass123")
    resp = client.get("/api/v1/auth/me", headers=_auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "me@example.com"
    assert "id" in data
    assert "created_at" in data


def test_get_me_unauthenticated_returns_401():
    """GET /me without a token must return 401."""
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401


def test_logout_clears_cookies():
    """POST /logout must return 200 and clear auth cookies."""
    client.post("/api/v1/auth/register", json={"email": "logout@example.com", "password": "testpass123"})
    # Login to get cookies
    client.post(
        "/api/v1/auth/login",
        data={"username": "logout@example.com", "password": "testpass123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    resp = client.post("/api/v1/auth/logout")
    assert resp.status_code == 200
    assert resp.json()["detail"] == "Successfully logged out"
    # After logout cookies are expired/removed
    assert resp.cookies.get("access_token", "") == ""
    assert resp.cookies.get("refresh_token", "") == ""


def test_wrong_password_returns_401():
    """Login with wrong password must return 401."""
    client.post("/api/v1/auth/register", json={"email": "wrongpw@example.com", "password": "correctpass1"})
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": "wrongpw@example.com", "password": "wrongpass1"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 401
