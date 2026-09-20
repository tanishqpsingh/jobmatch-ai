from fastapi import APIRouter, File, UploadFile, status
from backend.app.schemas.resume import ResumeParseResponse
from backend.app.services.file_validation import validate_file
from backend.app.services.resume_parser import parse_resume

router = APIRouter(prefix="/resumes", tags=["Resumes"])


@router.post(
    "/parse",
    response_model=ResumeParseResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload and parse a PDF or DOCX resume",
    description=(
        "Safely validates uploaded PDF or DOCX files (checking file size, extension, "
        "and binary header signature), extracts raw text using PyMuPDF or python-docx, "
        "and returns a structured representation."
    ),
)
async def parse_resume_endpoint(file: UploadFile = File(...)) -> ResumeParseResponse:
    """Endpoint for uploading and parsing resume documents."""
    # Read file content safely in memory
    content = await file.read()

    # Validate file size, extension, magic bytes, and sanitize filename
    safe_filename, extension = validate_file(
        filename=file.filename or "unnamed_resume",
        content=content,
        mime_type=file.content_type,
    )

    # Parse resume and return structured schema
    parsed_resume = parse_resume(
        filename=safe_filename,
        content=content,
        extension=extension,
    )

    return parsed_resume
