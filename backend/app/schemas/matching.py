from typing import List, Literal
from pydantic import BaseModel, Field
from backend.app.schemas.resume import ResumeParseResponse
from backend.app.schemas.job import JobAnalyzeResponse

CompatibilityStatus = Literal["match", "partial_match", "mismatch", "insufficient_information"]


class CompatibilityAnalysis(BaseModel):
    """Detailed compatibility status for education or experience."""

    status: CompatibilityStatus = Field(
        ...,
        description="Compatibility status: match, partial_match, mismatch, or insufficient_information.",
    )
    details: str = Field(
        ...,
        description="Human-readable explanation of the comparison.",
    )


class MatchAnalyzeRequest(BaseModel):
    """Request payload containing parsed resume and analyzed job description."""

    resume: ResumeParseResponse = Field(..., description="Parsed resume data object")
    job: JobAnalyzeResponse = Field(..., description="Analyzed job description data object")


class MatchAnalyzeResponse(BaseModel):
    """Structured response output for resume to job comparison analysis."""

    matching_skills: List[str] = Field(default_factory=list, description="Required skills present in resume")
    missing_required_skills: List[str] = Field(default_factory=list, description="Required skills missing from resume")
    missing_preferred_skills: List[str] = Field(default_factory=list, description="Preferred skills missing from resume")
    matching_technologies: List[str] = Field(default_factory=list, description="Job technologies present in resume")
    missing_technologies: List[str] = Field(default_factory=list, description="Job technologies missing from resume")
    education_analysis: CompatibilityAnalysis = Field(..., description="Education compatibility analysis")
    experience_analysis: CompatibilityAnalysis = Field(..., description="Experience compatibility analysis")
    matching_keywords: List[str] = Field(default_factory=list, description="Job keywords present in resume")
    missing_keywords: List[str] = Field(default_factory=list, description="Job keywords missing from resume")
    summary: str = Field(..., description="Human-readable summary of the comparison")
