from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


# --- 1. Bullet Improvement ---
class BulletImproveRequest(BaseModel):
    """Request payload for resume bullet enhancement."""

    bullet_text: str = Field(..., min_length=5, max_length=1000, description="Existing resume bullet point text")
    job_context: Optional[str] = Field(default=None, max_length=2000, description="Optional target job context or title")

    @field_validator("bullet_text")
    @classmethod
    def validate_bullet(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Bullet text cannot be empty or whitespace-only.")
        return value.strip()


class BulletImproveResponse(BaseModel):
    """Response payload for enhanced resume bullet point."""

    original_bullet: str = Field(..., description="Original bullet text provided")
    improved_bullet: str = Field(..., description="Factually preserved, action-oriented improved bullet")
    explanation: str = Field(..., description="Explanation of clarity and impact enhancements made")
    factual_note: str = Field(..., description="Confirmation of factual preservation guarantee")


# --- 2. Skill Explanation ---
class SkillExplainRequest(BaseModel):
    """Request payload for missing skill explanation."""

    skill_name: str = Field(..., min_length=1, max_length=100, description="Missing skill or competency name")
    job_context: Optional[str] = Field(default=None, max_length=2000, description="Optional job description context")

    @field_validator("skill_name")
    @classmethod
    def validate_skill(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Skill name cannot be empty.")
        return value.strip()


class SkillExplainResponse(BaseModel):
    """Response payload for missing skill explanation and learning roadmap."""

    skill_name: str = Field(..., description="Target skill name")
    summary: str = Field(..., description="High-level overview of what the skill is")
    why_relevant: str = Field(..., description="Why this skill matters for the target job role")
    core_concepts: List[str] = Field(default_factory=list, description="Key fundamental concepts to master")
    learning_path: List[str] = Field(default_factory=list, description="Step-by-step beginner learning roadmap")
    project_ideas: List[str] = Field(default_factory=list, description="Practical project ideas to demonstrate proficiency")


# --- 3. Interview Questions ---
class InterviewQuestionItem(BaseModel):
    """Single generated interview question object."""

    category: str = Field(..., description="Technical, Behavioral, Role-Specific, or Resume-Based")
    question: str = Field(..., description="Generated interview question text")
    tip_or_context: str = Field(..., description="Answering strategy or context tip")


class InterviewQuestionsRequest(BaseModel):
    """Request payload for tailored interview question generation."""

    job_title: Optional[str] = Field(default=None, max_length=200, description="Target job title")
    job_description: Optional[str] = Field(default=None, max_length=10000, description="Optional job posting description")
    resume_skills: List[str] = Field(default_factory=list, description="Candidate resume skills")


class InterviewQuestionsResponse(BaseModel):
    """Response payload containing generated interview questions."""

    job_title: Optional[str] = Field(default=None, description="Job title context")
    questions: List[InterviewQuestionItem] = Field(default_factory=list, description="List of generated questions")


# --- 4. Interview Preparation Guide ---
class InterviewPrepRequest(BaseModel):
    """Request payload for job-specific interview preparation guide."""

    job_title: str = Field(..., min_length=1, max_length=200, description="Target job title")
    required_skills: List[str] = Field(default_factory=list, description="Required skills from job posting")
    missing_skills: List[str] = Field(default_factory=list, description="Missing skills identified from matching")

    @field_validator("job_title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Job title cannot be empty.")
        return value.strip()


class InterviewPrepResponse(BaseModel):
    """Response payload containing job-specific interview prep guide."""

    job_title: str = Field(..., description="Target job title")
    revision_topics: List[str] = Field(default_factory=list, description="Core technical topics to revise")
    technical_focus_areas: List[str] = Field(default_factory=list, description="Likely technical evaluation areas")
    resume_questions: List[str] = Field(default_factory=list, description="Questions likely asked about experience")
    practice_questions: List[str] = Field(default_factory=list, description="Suggested technical and role practice questions")
    prep_strategy: str = Field(..., description="Strategic interview preparation summary")


# --- 5. Technology Explanation ---
class TechExplainRequest(BaseModel):
    """Request payload for technology explanation."""

    technology_name: str = Field(..., min_length=1, max_length=100, description="Technology name (e.g. Docker, PostgreSQL)")
    job_context: Optional[str] = Field(default=None, max_length=2000, description="Optional job role context")

    @field_validator("technology_name")
    @classmethod
    def validate_tech(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Technology name cannot be empty.")
        return value.strip()


class TechExplainResponse(BaseModel):
    """Response payload explaining a technology for a job role."""

    technology_name: str = Field(..., description="Target technology name")
    simple_explanation: str = Field(..., description="Clear, plain-language explanation of the technology")
    relevance_to_role: str = Field(..., description="Why this technology is used in the role context")
    core_concepts: List[str] = Field(default_factory=list, description="Fundamental building blocks to understand")
    first_steps: List[str] = Field(default_factory=list, description="Immediate practical steps to start learning")
    practical_exercise: str = Field(..., description="A simple hands-on starter exercise")


# --- 6. Study Plan Generator ---
class StudyWeekItem(BaseModel):
    """Structured weekly study plan milestone."""

    week_number: int = Field(..., description="Week number in sequence")
    focus_area: str = Field(..., description="Primary learning focus for the week")
    topics: List[str] = Field(default_factory=list, description="Specific topics and modules to cover")
    practical_milestone: str = Field(..., description="Deliverable or hands-on milestone for the week")


class StudyPlanRequest(BaseModel):
    """Request payload for structured study plan generation."""

    missing_skills: List[str] = Field(..., min_length=1, max_length=20, description="List of missing skills to learn")
    available_weeks: int = Field(default=4, ge=1, le=12, description="Target duration in weeks (1-12)")
    hours_per_week: Optional[int] = Field(default=10, ge=1, le=40, description="Estimated study hours per week")


class StudyPlanResponse(BaseModel):
    """Response payload containing weekly study plan roadmap."""

    missing_skills: List[str] = Field(default_factory=list, description="Target missing skills being addressed")
    total_weeks: int = Field(..., description="Duration of study plan in weeks")
    weekly_plan: List[StudyWeekItem] = Field(default_factory=list, description="Structured week-by-week learning roadmap")
