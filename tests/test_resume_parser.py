import io
import pymupdf as fitz  # PyMuPDF
import docx
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def create_sample_pdf_bytes(text: str = "Jane Doe\njane.doe@example.com\n(555) 123-4567\n\nEducation\nB.S. Computer Science\n\nSkills\nPython, FastAPI, React, PostgreSQL\n\nExperience\nSoftware Engineer at Tech Corp") -> bytes:
    """Helper to generate valid PDF binary content in memory using PyMuPDF."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), text)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def create_sample_docx_bytes(text: str = "John Smith\njohn.smith@example.com\n+1 555-987-6543\n\nEducation\nM.S. Data Science\n\nSkills\nPython, PyTorch, PyMuPDF\n\nExperience\nAI Researcher at AI Lab") -> bytes:
    """Helper to generate valid DOCX binary content in memory using python-docx."""
    doc = docx.Document()
    for paragraph in text.split("\n"):
        doc.add_paragraph(paragraph)
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()


# 1. Valid PDF Parsing Test
def test_parse_valid_pdf():
    pdf_bytes = create_sample_pdf_bytes()
    response = client.post(
        "/api/v1/resumes/parse",
        files={"file": ("resume.pdf", pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "resume.pdf"
    assert data["email"] == "jane.doe@example.com"
    assert data["phone"] == "(555) 123-4567"
    assert "Jane Doe" in data["raw_text"]
    assert isinstance(data["skills"], list)
    assert isinstance(data["education"], list)


# 2. Valid DOCX Parsing Test
def test_parse_valid_docx():
    docx_bytes = create_sample_docx_bytes()
    response = client.post(
        "/api/v1/resumes/parse",
        files={"file": ("resume.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "resume.docx"
    assert data["email"] == "john.smith@example.com"
    assert data["phone"] == "+1 555-987-6543"
    assert "John Smith" in data["raw_text"]
    assert isinstance(data["skills"], list)


# 3. Unsupported File Type Test (.txt / .exe)
def test_parse_unsupported_file_extension():
    response = client.post(
        "/api/v1/resumes/parse",
        files={"file": ("document.txt", b"Hello World text file content", "text/plain")},
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


# 4. Oversized File Test (> 5MB)
def test_parse_oversized_file():
    # Generate 5.1 MB dummy PDF header content
    oversized_bytes = b"%PDF-1.5\n" + b"A" * (5 * 1024 * 1024 + 100)
    response = client.post(
        "/api/v1/resumes/parse",
        files={"file": ("huge_resume.pdf", oversized_bytes, "application/pdf")},
    )
    assert response.status_code == 413
    assert "File size exceeds maximum" in response.json()["detail"]


# 5. Empty File Test (0 bytes)
def test_parse_empty_file():
    response = client.post(
        "/api/v1/resumes/parse",
        files={"file": ("empty.pdf", b"", "application/pdf")},
    )
    assert response.status_code == 400
    assert "File is empty" in response.json()["detail"]


# 6. Malformed PDF Document Test
def test_parse_malformed_pdf():
    # PDF magic header present, but corrupt garbage binary content afterwards
    corrupt_pdf = b"%PDF-1.4\nCorrupt garbage binary content 12345"
    response = client.post(
        "/api/v1/resumes/parse",
        files={"file": ("corrupt.pdf", corrupt_pdf, "application/pdf")},
    )
    assert response.status_code == 400
    assert "Malformed" in response.json()["detail"] or "corrupt" in response.json()["detail"].lower()


# 7. Malformed DOCX Document Test
def test_parse_malformed_docx():
    # ZIP magic header present, but corrupt binary content
    corrupt_docx = b"PK\x03\x04Corrupt zip binary content"
    response = client.post(
        "/api/v1/resumes/parse",
        files={"file": ("corrupt.docx", corrupt_docx, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )
    assert response.status_code == 400
    assert "Malformed" in response.json()["detail"] or "corrupt" in response.json()["detail"].lower()


# 8. Filename / Path Traversal Attempt Test
def test_parse_path_traversal_filename():
    pdf_bytes = create_sample_pdf_bytes()
    response = client.post(
        "/api/v1/resumes/parse",
        files={"file": ("../../../../etc/passwd.pdf", pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 200
    data = response.json()
    # Path components must be sanitized to basename only
    assert data["filename"] == "passwd.pdf"
    assert "/" not in data["filename"]
    assert "\\" not in data["filename"]


# 9. Restricted Filename (.env attempt) Test
def test_parse_restricted_filename():
    response = client.post(
        "/api/v1/resumes/parse",
        files={"file": (".env.pdf", create_sample_pdf_bytes(), "application/pdf")},
    )
    assert response.status_code == 400
    assert "Invalid or restricted filename" in response.json()["detail"]


# 10. Structured Response Schema Validation Test
def test_parse_structured_schema_fields():
    pdf_bytes = create_sample_pdf_bytes()
    response = client.post(
        "/api/v1/resumes/parse",
        files={"file": ("sample.pdf", pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 200
    data = response.json()
    expected_keys = {
        "filename", "name", "email", "phone",
        "education", "skills", "experience",
        "projects", "certifications", "raw_text"
    }
    assert expected_keys.issubset(data.keys())
