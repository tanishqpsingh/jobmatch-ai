from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

SAMPLE_RESUME = {
    "filename": "sample_resume.pdf",
    "name": "Jane Doe",
    "email": "jane@example.com",
    "phone": "(555) 123-4567",
    "education": ["Bachelor of Science in Computer Science"],
    "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Git"],
    "experience": [
        "Software Engineer at Tech Corp (3 years)",
        "Junior Developer at Startup (2 years)"
    ],
    "projects": ["Build JobMatch AI platform"],
    "certifications": ["AWS Certified Developer"],
    "raw_text": "Jane Doe. BS in Computer Science. 5 years experience with Python, FastAPI, PostgreSQL, Docker, Git."
}

SAMPLE_JOB = {
    "job_title": "Backend Engineer",
    "company": "Acme Corp",
    "required_skills": ["Python", "FastAPI", "PostgreSQL", "Kubernetes"],
    "preferred_skills": ["AWS", "Redis"],
    "technologies": ["Python", "FastAPI", "PostgreSQL", "Docker", "Kubernetes"],
    "education_requirements": ["Bachelor of Science in Computer Science or related field"],
    "experience_requirements": ["3+ years of software engineering experience"],
    "keywords": ["Backend", "Microservices", "REST API", "Database"]
}


# 1. Exact & Case-Insensitive Skill Match Test
def test_matching_exact_and_case_insensitive_skills():
    resume = dict(SAMPLE_RESUME)
    resume["skills"] = ["python", "FASTAPI", "  postgresql  "]

    job = dict(SAMPLE_JOB)
    job["required_skills"] = ["Python", "FastAPI", "PostgreSQL", "Go"]

    payload = {"resume": resume, "job": job}

    response = client.post("/api/v1/matching/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "Python" in data["matching_skills"] or "python" in data["matching_skills"]
    assert len(data["matching_skills"]) == 3
    assert data["missing_required_skills"] == ["Go"]


# 2. Whitespace Normalization & Duplicate Skill Handling Test
def test_matching_whitespace_and_duplicates():
    resume = dict(SAMPLE_RESUME)
    resume["skills"] = [" Python ", "Python", "fastapi"]

    job = dict(SAMPLE_JOB)
    job["required_skills"] = ["Python", "Python", "FastAPI"]

    payload = {"resume": resume, "job": job}

    response = client.post("/api/v1/matching/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert len(data["matching_skills"]) == 2  # Deduplicated Python & FastAPI
    assert data["missing_required_skills"] == []


# 3. Missing Required & Preferred Skills Test
def test_matching_missing_skills():
    resume = dict(SAMPLE_RESUME)
    resume["skills"] = ["HTML", "CSS", "JavaScript"]
    resume["raw_text"] = "Frontend developer skilled in HTML, CSS, and JavaScript."
    resume["certifications"] = []

    job = dict(SAMPLE_JOB)
    job["required_skills"] = ["Python", "FastAPI"]
    job["preferred_skills"] = ["AWS", "GraphQL"]

    payload = {"resume": resume, "job": job}

    response = client.post("/api/v1/matching/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["matching_skills"] == []
    assert data["missing_required_skills"] == ["Python", "FastAPI"]
    assert data["missing_preferred_skills"] == ["AWS", "GraphQL"]


# 4. Technology Matching Test
def test_matching_technologies():
    resume = dict(SAMPLE_RESUME)
    job = dict(SAMPLE_JOB)

    payload = {"resume": resume, "job": job}

    response = client.post("/api/v1/matching/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "Docker" in data["matching_technologies"]
    assert "Kubernetes" in data["missing_technologies"]


# 5. Keyword Matching Test
def test_matching_keywords():
    resume = dict(SAMPLE_RESUME)
    resume["raw_text"] = "Software Engineer experienced in building REST API applications with PostgreSQL database."

    job = dict(SAMPLE_JOB)
    job["keywords"] = ["REST API", "Database", "GraphQL"]

    payload = {"resume": resume, "job": job}

    response = client.post("/api/v1/matching/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "REST API" in data["matching_keywords"]
    assert "Database" in data["matching_keywords"]
    assert "GraphQL" in data["missing_keywords"]


# 6. Education Match Test
def test_matching_education_match():
    resume = dict(SAMPLE_RESUME)
    resume["education"] = ["Master of Science in Computer Science"]

    job = dict(SAMPLE_JOB)
    job["education_requirements"] = ["Bachelor's Degree in Computer Science"]

    payload = {"resume": resume, "job": job}

    response = client.post("/api/v1/matching/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["education_analysis"]["status"] == "match"


# 7. Education Insufficient Information Test
def test_matching_education_insufficient_info():
    resume = dict(SAMPLE_RESUME)
    resume["education"] = []
    resume["raw_text"] = "No education mentioned"

    job = dict(SAMPLE_JOB)

    payload = {"resume": resume, "job": job}

    response = client.post("/api/v1/matching/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["education_analysis"]["status"] == "insufficient_information"


# 8. Experience Match Test
def test_matching_experience_match():
    resume = dict(SAMPLE_RESUME)
    resume["experience"] = ["Software Engineer (4 years)", "Lead Developer (2 years)"]

    job = dict(SAMPLE_JOB)
    job["experience_requirements"] = ["3+ years of experience"]

    payload = {"resume": resume, "job": job}

    response = client.post("/api/v1/matching/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["experience_analysis"]["status"] == "match"


# 9. Experience Insufficient Information Test
def test_matching_experience_insufficient_info():
    resume = dict(SAMPLE_RESUME)
    resume["experience"] = []
    resume["raw_text"] = ""

    job = dict(SAMPLE_JOB)
    job["experience_requirements"] = []

    payload = {"resume": resume, "job": job}

    response = client.post("/api/v1/matching/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["experience_analysis"]["status"] == "insufficient_information"


# 10. Empty Resume Skills & Empty Job Skills Test
def test_matching_empty_skills():
    resume = dict(SAMPLE_RESUME)
    resume["skills"] = []

    job = dict(SAMPLE_JOB)
    job["required_skills"] = []

    payload = {"resume": resume, "job": job}

    response = client.post("/api/v1/matching/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["matching_skills"] == []
    assert data["missing_required_skills"] == []


# 11. No False-Positive Substring Match Test (Java vs JavaScript, C vs CSS)
def test_matching_no_false_positive_substring():
    resume = dict(SAMPLE_RESUME)
    resume["skills"] = ["JavaScript", "CSS", "HTML"]
    resume["raw_text"] = "Senior Web Developer specializing in JavaScript and CSS styling."

    job = dict(SAMPLE_JOB)
    job["required_skills"] = ["Java", "C"]  # Java should NOT match JavaScript, C should NOT match CSS

    payload = {"resume": resume, "job": job}

    response = client.post("/api/v1/matching/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "Java" not in data["matching_skills"]
    assert "C" not in data["matching_skills"]
    assert data["missing_required_skills"] == ["Java", "C"]


# 12. Invalid Request Structure Test
def test_matching_invalid_structure():
    payload = {"resume": "not_an_object"}
    response = client.post("/api/v1/matching/analyze", json=payload)
    assert response.status_code == 422


# 13. Mock Gemini AI Explanation Success & Fallback Test
@patch("backend.app.services.matching_engine.get_settings")
@patch("backend.app.services.matching_engine.genai.Client")
def test_matching_ai_explanation_success(mock_genai_client, mock_get_settings):
    mock_settings = MagicMock()
    mock_settings.GEMINI_API_KEY = "dummy_key_123"
    mock_settings.GEMINI_MODEL = "gemini-1.5-pro"
    mock_get_settings.return_value = mock_settings

    mock_response = MagicMock()
    mock_response.text = "AI Refined Summary: Excellent match for backend requirements."
    mock_client_inst = MagicMock()
    mock_client_inst.models.generate_content.return_value = mock_response
    mock_genai_client.return_value = mock_client_inst

    payload = {"resume": SAMPLE_RESUME, "job": SAMPLE_JOB}
    response = client.post("/api/v1/matching/analyze", json=payload)
    assert response.status_code == 200
    assert response.json()["summary"] == "AI Refined Summary: Excellent match for backend requirements."
