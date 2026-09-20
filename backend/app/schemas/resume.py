from typing import List, Optional
from pydantic import BaseModel, Field


class ResumeParseResponse(BaseModel):
    """Structured response schema for parsed resume documents."""

    filename: str = Field(description="Sanitized uploaded filename")
    name: Optional[str] = Field(default=None, description="Extracted candidate name")
    email: Optional[str] = Field(default=None, description="Extracted candidate email address")
    phone: Optional[str] = Field(default=None, description="Extracted candidate phone number")
    education: List[str] = Field(default_factory=list, description="Extracted education details")
    skills: List[str] = Field(default_factory=list, description="Extracted skills and technologies")
    experience: List[str] = Field(default_factory=list, description="Extracted professional experience items")
    projects: List[str] = Field(default_factory=list, description="Extracted project highlights")
    certifications: List[str] = Field(default_factory=list, description="Extracted certifications and credentials")
    raw_text: str = Field(default="", description="Normalized full text of the resume")
