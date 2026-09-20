from fastapi import APIRouter, status
from backend.app.schemas.job import JobAnalyzeRequest, JobAnalyzeResponse
from backend.app.services.job_analyzer import analyze_job_description_service

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post(
    "/analyze",
    response_model=JobAnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze job description and extract requirements",
    description=(
        "Validates input job description, extracts required and preferred skills, "
        "technologies, education, experience, and keywords using Google Gemini AI, "
        "and returns a structured JSON schema."
    ),
)
async def analyze_job_endpoint(request: JobAnalyzeRequest) -> JobAnalyzeResponse:
    """Endpoint to analyze job descriptions and extract structured requirements."""
    return analyze_job_description_service(request)
