from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class JobAnalyzeRequest(BaseModel):
    """Request schema for job description analysis."""

    job_description: str = Field(
        ...,
        min_length=10,
        max_length=50000,
        description="Raw text content of the job description to analyze.",
    )
    company: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Optional company name offering the job.",
    )
    job_title: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Optional job title or role name.",
    )

    @field_validator("job_description")
    @classmethod
    def validate_non_whitespace(cls, value: str) -> str:
        """Ensure job description is not empty or containing only whitespace."""
        if not value or not value.strip():
            raise ValueError("Job description cannot be empty or whitespace-only.")
        return value.strip()

    @field_validator("company", "job_title")
    @classmethod
    def sanitize_optional_strings(cls, value: Optional[str]) -> Optional[str]:
        """Strip leading/trailing whitespace from optional text fields."""
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned if cleaned else None


class JobAnalyzeResponse(BaseModel):
    """Structured response schema representing analyzed job requirements."""

    job_title: Optional[str] = Field(default=None, description="Extracted job title")
    company: Optional[str] = Field(default=None, description="Extracted company name")
    required_skills: List[str] = Field(default_factory=list, description="Explicitly required skills")
    preferred_skills: List[str] = Field(default_factory=list, description="Nice-to-have or preferred skills")
    technologies: List[str] = Field(default_factory=list, description="Tools, frameworks, and technologies")
    education_requirements: List[str] = Field(default_factory=list, description="Education and degree requirements")
    experience_requirements: List[str] = Field(default_factory=list, description="Experience requirements")
    keywords: List[str] = Field(default_factory=list, description="Important domain & industry keywords")
