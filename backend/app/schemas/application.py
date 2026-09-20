from datetime import date, datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator

ALLOWED_STATUSES = ("saved", "applied", "screening", "interview", "offer", "rejected", "withdrawn")
ApplicationStatus = Literal["saved", "applied", "screening", "interview", "offer", "rejected", "withdrawn"]


class ApplicationBase(BaseModel):
    """Base schema for application properties."""

    company: str = Field(..., min_length=1, max_length=200, description="Company name")
    job_title: str = Field(..., min_length=1, max_length=200, description="Job title or role")
    job_description: Optional[str] = Field(default=None, max_length=50000, description="Optional raw job description")
    application_date: Optional[date] = Field(default_factory=date.today, description="Date applied")
    status: ApplicationStatus = Field(default="saved", description="Current application status")
    interview_date: Optional[datetime] = Field(default=None, description="Scheduled interview date and time")
    notes: Optional[str] = Field(default=None, max_length=10000, description="Personal application notes")

    @field_validator("company", "job_title")
    @classmethod
    def validate_non_empty_string(cls, value: str) -> str:
        """Validate string is not empty or whitespace-only."""
        if not value or not value.strip():
            raise ValueError("Field cannot be empty or whitespace-only.")
        return value.strip()


class ApplicationCreate(ApplicationBase):
    """Creation payload for new job applications."""

    pass


class ApplicationUpdate(BaseModel):
    """Partial update payload for existing job applications."""

    company: Optional[str] = Field(default=None, min_length=1, max_length=200)
    job_title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    job_description: Optional[str] = Field(default=None, max_length=50000)
    application_date: Optional[date] = None
    status: Optional[ApplicationStatus] = None
    interview_date: Optional[datetime] = None
    notes: Optional[str] = Field(default=None, max_length=10000)

    @field_validator("company", "job_title")
    @classmethod
    def validate_optional_strings(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Field cannot be empty or whitespace-only.")
        return cleaned


class ApplicationResponse(ApplicationBase):
    """Output schema for tracked job application records."""

    id: int = Field(..., description="Unique application ID")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Record last updated timestamp")

    model_config = {"from_attributes": True}


class ApplicationSummaryResponse(BaseModel):
    """Summary stats schema for dashboard reporting."""

    total: int = 0
    saved: int = 0
    applied: int = 0
    screening: int = 0
    interview: int = 0
    offer: int = 0
    rejected: int = 0
    withdrawn: int = 0
