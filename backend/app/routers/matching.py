from fastapi import APIRouter, status
from backend.app.schemas.matching import MatchAnalyzeRequest, MatchAnalyzeResponse
from backend.app.services.matching_engine import compute_match

router = APIRouter(prefix="/matching", tags=["Matching"])


@router.post(
    "/analyze",
    response_model=MatchAnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Compare parsed resume against analyzed job description",
    description=(
        "Performs a deterministic, explainable comparison between a candidate's "
        "parsed resume and an analyzed job description. Evaluates skill overlaps, "
        "missing required/preferred skills, technology matches, keyword overlaps, "
        "education compatibility, and experience requirements."
    ),
)
async def analyze_match_endpoint(request: MatchAnalyzeRequest) -> MatchAnalyzeResponse:
    """Endpoint for resume to job matching analysis."""
    return compute_match(request)
