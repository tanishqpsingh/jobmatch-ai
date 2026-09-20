from fastapi import APIRouter, status
from backend.app.schemas.career import (
    BulletImproveRequest, BulletImproveResponse,
    SkillExplainRequest, SkillExplainResponse,
    InterviewQuestionsRequest, InterviewQuestionsResponse,
    InterviewPrepRequest, InterviewPrepResponse,
    TechExplainRequest, TechExplainResponse,
    StudyPlanRequest, StudyPlanResponse,
)
from backend.app.services import career_service

router = APIRouter(prefix="/career", tags=["Career Assistant"])


@router.post(
    "/improve-bullet",
    response_model=BulletImproveResponse,
    status_code=status.HTTP_200_OK,
    summary="Enhance a resume bullet point",
    description="Enhances phrasing and action verbs for a resume bullet point while strictly preserving factual scope.",
)
def improve_bullet_endpoint(request: BulletImproveRequest) -> BulletImproveResponse:
    """Enhance resume bullet point."""
    return career_service.improve_bullet_service(request)


@router.post(
    "/explain-skill",
    response_model=SkillExplainResponse,
    status_code=status.HTTP_200_OK,
    summary="Explain a missing skill and learning roadmap",
    description="Explains what a missing skill is, why it matters for a role, and provides a beginner learning roadmap.",
)
def explain_skill_endpoint(request: SkillExplainRequest) -> SkillExplainResponse:
    """Explain a missing skill."""
    return career_service.explain_skill_service(request)


@router.post(
    "/interview-questions",
    response_model=InterviewQuestionsResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate tailored interview questions",
    description="Generates technical, behavioral, and role-specific interview questions based on job and candidate skills.",
)
def generate_interview_questions_endpoint(request: InterviewQuestionsRequest) -> InterviewQuestionsResponse:
    """Generate interview questions."""
    return career_service.generate_interview_questions_service(request)


@router.post(
    "/interview-prep",
    response_model=InterviewPrepResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate job interview prep guide",
    description="Generates revision topics, technical focus areas, and practice questions tailored to a specific job.",
)
def generate_interview_prep_endpoint(request: InterviewPrepRequest) -> InterviewPrepResponse:
    """Generate interview prep guide."""
    return career_service.generate_interview_prep_service(request)


@router.post(
    "/explain-technology",
    response_model=TechExplainResponse,
    status_code=status.HTTP_200_OK,
    summary="Explain a technology for a job role",
    description="Provides plain-language explanation, core concepts, and practical exercises for a specific technology.",
)
def explain_technology_endpoint(request: TechExplainRequest) -> TechExplainResponse:
    """Explain technology for a job role."""
    return career_service.explain_technology_service(request)


@router.post(
    "/study-plan",
    response_model=StudyPlanResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate a week-by-week study plan",
    description="Generates a structured week-by-week study plan to master missing skills required for a job role.",
)
def generate_study_plan_endpoint(request: StudyPlanRequest) -> StudyPlanResponse:
    """Generate structured study plan."""
    return career_service.generate_study_plan_service(request)
