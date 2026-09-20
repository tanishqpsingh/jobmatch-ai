import json
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

SAMPLE_JOB_TEXT = """
We are seeking a Senior Backend Engineer to join Acme Corp.
Requirements:
- 5+ years of experience with Python and FastAPI.
- Deep knowledge of PostgreSQL and relational database design.
- Experience with Docker and CI/CD pipelines.

Preferred Qualifications:
- Experience with Google Gemini API or LLMs.
- Degree in Computer Science or equivalent.
"""

SAMPLE_MOCK_GEMINI_PAYLOAD = {
    "job_title": "Senior Backend Engineer",
    "company": "Acme Corp",
    "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "CI/CD"],
    "preferred_skills": ["Google Gemini API", "LLMs"],
    "technologies": ["Python", "FastAPI", "PostgreSQL", "Docker", "Git"],
    "education_requirements": ["Degree in Computer Science or equivalent"],
    "experience_requirements": ["5+ years of experience"],
    "keywords": ["Backend", "Senior", "API", "Database", "Containerization"]
}


# 1. Valid Job Description with Mocked Gemini API Success
@patch("backend.app.services.job_analyzer.get_settings")
@patch("backend.app.services.job_analyzer.genai.Client")
def test_analyze_job_valid_success(mock_genai_client, mock_get_settings):
    # Mock settings to provide a dummy API key
    mock_settings = MagicMock()
    mock_settings.GEMINI_API_KEY = "dummy_mock_api_key_12345"
    mock_settings.GEMINI_MODEL = "gemini-2.5-flash"
    mock_get_settings.return_value = mock_settings

    # Mock Gemini response object
    mock_response = MagicMock()
    mock_response.text = json.dumps(SAMPLE_MOCK_GEMINI_PAYLOAD)
    mock_client_instance = MagicMock()
    mock_client_instance.models.generate_content.return_value = mock_response
    mock_genai_client.return_value = mock_client_instance

    payload = {
        "job_description": SAMPLE_JOB_TEXT,
        "company": "Acme Corp",
        "job_title": "Senior Backend Engineer"
    }

    response = client.post("/api/v1/jobs/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["job_title"] == "Senior Backend Engineer"
    assert data["company"] == "Acme Corp"
    assert "Python" in data["required_skills"]
    assert "LLMs" in data["preferred_skills"]
    assert isinstance(data["technologies"], list)
    assert isinstance(data["education_requirements"], list)
    assert isinstance(data["experience_requirements"], list)
    assert isinstance(data["keywords"], list)


# 2. Empty Job Description Rejection Test
def test_analyze_job_empty_description():
    payload = {"job_description": ""}
    response = client.post("/api/v1/jobs/analyze", json=payload)
    assert response.status_code == 422  # Pydantic validation error


# 3. Whitespace-only Job Description Rejection Test
def test_analyze_job_whitespace_description():
    payload = {"job_description": "              "}
    response = client.post("/api/v1/jobs/analyze", json=payload)
    assert response.status_code == 422  # Pydantic validation error


# 4. Excessively Large Job Description Rejection Test (> 50,000 chars)
def test_analyze_job_oversized_description():
    oversized_text = "Python Developer " * 5000  # > 80,000 chars
    payload = {"job_description": oversized_text}
    response = client.post("/api/v1/jobs/analyze", json=payload)
    assert response.status_code == 422


# 5. Optional Company Field Processing Test
@patch("backend.app.services.job_analyzer.get_settings")
@patch("backend.app.services.job_analyzer.genai.Client")
def test_analyze_job_optional_company(mock_genai_client, mock_get_settings):
    mock_settings = MagicMock()
    mock_settings.GEMINI_API_KEY = "dummy_mock_api_key_12345"
    mock_settings.GEMINI_MODEL = "gemini-2.5-flash"
    mock_get_settings.return_value = mock_settings

    mock_payload_no_company = dict(SAMPLE_MOCK_GEMINI_PAYLOAD)
    mock_payload_no_company["company"] = None

    mock_response = MagicMock()
    mock_response.text = json.dumps(mock_payload_no_company)
    mock_client_instance = MagicMock()
    mock_client_instance.models.generate_content.return_value = mock_response
    mock_genai_client.return_value = mock_client_instance

    payload = {
        "job_description": SAMPLE_JOB_TEXT,
        "company": "   Globex Inc   "
    }

    response = client.post("/api/v1/jobs/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["company"] == "Globex Inc"  # Sanitized whitespace


# 6. Optional Job Title Field Processing Test
@patch("backend.app.services.job_analyzer.get_settings")
@patch("backend.app.services.job_analyzer.genai.Client")
def test_analyze_job_optional_job_title(mock_genai_client, mock_get_settings):
    mock_settings = MagicMock()
    mock_settings.GEMINI_API_KEY = "dummy_mock_api_key_12345"
    mock_settings.GEMINI_MODEL = "gemini-2.5-flash"
    mock_get_settings.return_value = mock_settings

    mock_payload_no_title = dict(SAMPLE_MOCK_GEMINI_PAYLOAD)
    mock_payload_no_title["job_title"] = None

    mock_response = MagicMock()
    mock_response.text = json.dumps(mock_payload_no_title)
    mock_client_instance = MagicMock()
    mock_client_instance.models.generate_content.return_value = mock_response
    mock_genai_client.return_value = mock_client_instance

    payload = {
        "job_description": SAMPLE_JOB_TEXT,
        "job_title": "Lead Software Architect"
    }

    response = client.post("/api/v1/jobs/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["job_title"] == "Lead Software Architect"


# 7. Structured Response Validation Test
@patch("backend.app.services.job_analyzer.get_settings")
@patch("backend.app.services.job_analyzer.genai.Client")
def test_analyze_job_structured_schema(mock_genai_client, mock_get_settings):
    mock_settings = MagicMock()
    mock_settings.GEMINI_API_KEY = "dummy_mock_api_key_12345"
    mock_settings.GEMINI_MODEL = "gemini-2.5-flash"
    mock_get_settings.return_value = mock_settings

    mock_response = MagicMock()
    mock_response.text = json.dumps(SAMPLE_MOCK_GEMINI_PAYLOAD)
    mock_client_instance = MagicMock()
    mock_client_instance.models.generate_content.return_value = mock_response
    mock_genai_client.return_value = mock_client_instance

    payload = {"job_description": SAMPLE_JOB_TEXT}

    response = client.post("/api/v1/jobs/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    expected_keys = {
        "job_title", "company", "required_skills", "preferred_skills",
        "technologies", "education_requirements", "experience_requirements", "keywords"
    }
    assert expected_keys.issubset(data.keys())


# 8. Malformed Gemini Response Handling Test
@patch("backend.app.services.job_analyzer.get_settings")
@patch("backend.app.services.job_analyzer.genai.Client")
def test_analyze_job_malformed_gemini_json(mock_genai_client, mock_get_settings):
    mock_settings = MagicMock()
    mock_settings.GEMINI_API_KEY = "dummy_mock_api_key_12345"
    mock_settings.GEMINI_MODEL = "gemini-2.5-flash"
    mock_get_settings.return_value = mock_settings

    # Response is not valid JSON
    mock_response = MagicMock()
    mock_response.text = "This is non-JSON garbage returned by AI"
    mock_client_instance = MagicMock()
    mock_client_instance.models.generate_content.return_value = mock_response
    mock_genai_client.return_value = mock_client_instance

    payload = {"job_description": SAMPLE_JOB_TEXT}

    response = client.post("/api/v1/jobs/analyze", json=payload)
    assert response.status_code == 502
    assert "AI processing or response format error" in response.json()["detail"]


# 9. Gemini / API Failure Test
@patch("backend.app.services.job_analyzer.get_settings")
@patch("backend.app.services.job_analyzer.genai.Client")
def test_analyze_job_gemini_api_exception(mock_genai_client, mock_get_settings):
    mock_settings = MagicMock()
    mock_settings.GEMINI_API_KEY = "dummy_mock_api_key_12345"
    mock_settings.GEMINI_MODEL = "gemini-2.5-flash"
    mock_get_settings.return_value = mock_settings

    # Mock client throwing an unexpected exception (e.g. connection reset or internal error)
    mock_client_instance = MagicMock()
    mock_client_instance.models.generate_content.side_effect = RuntimeError("Connection connection_secret_key_123 refused")
    mock_genai_client.return_value = mock_client_instance

    payload = {"job_description": SAMPLE_JOB_TEXT}

    response = client.post("/api/v1/jobs/analyze", json=payload)
    assert response.status_code == 502
    # Ensure raw exception message containing connection secrets is hidden
    assert "connection_secret_key_123" not in response.json()["detail"]
    assert "AI processing or response format error" in response.json()["detail"]


# 10. Missing API Key Test (503 Service Unavailable)
@patch("backend.app.services.job_analyzer.get_settings")
def test_analyze_job_missing_api_key(mock_get_settings):
    mock_settings = MagicMock()
    mock_settings.GEMINI_API_KEY = ""  # Empty API key
    mock_get_settings.return_value = mock_settings

    payload = {"job_description": SAMPLE_JOB_TEXT}

    response = client.post("/api/v1/jobs/analyze", json=payload)
    assert response.status_code == 503
    assert "Gemini AI service is not configured" in response.json()["detail"]
