import json
import re
from typing import Dict, Any
from fastapi import HTTPException, status
from google import genai
from google.genai import types
from backend.app.config import get_settings
from backend.app.schemas.job import JobAnalyzeRequest, JobAnalyzeResponse

settings = get_settings()

SYSTEM_INSTRUCTION = """
You are an expert, objective job description parser.
Your job is to analyze the provided job description text and extract structured information.

CRITICAL INSTRUCTIONS:
1. Extract ONLY information that is explicitly stated or directly implied by the job description text.
2. Do NOT invent, assume, or fabricate any skills, tools, or requirements not present in the text.
3. Categorize requirements accurately:
   - required_skills: Mandatory skills or competencies.
   - preferred_skills: Nice-to-have, bonus, or preferred qualifications.
   - technologies: Programming languages, frameworks, databases, software, and cloud platforms.
   - education_requirements: Degrees, fields of study, or certifications mentioned for education.
   - experience_requirements: Years of experience or background requirements mentioned.
   - keywords: Core industry and role keywords.
4. Output MUST be valid JSON conforming strictly to the requested schema.
"""


def build_analysis_prompt(request: JobAnalyzeRequest) -> str:
    """Construct a clean, isolated prompt treating user input strictly as data."""
    context_parts = []
    if request.job_title:
        context_parts.append(f"Provided Job Title: {request.job_title}")
    if request.company:
        context_parts.append(f"Provided Company: {request.company}")

    context_str = "\n".join(context_parts) if context_parts else "None provided"

    prompt = f"""
[USER CONTEXT]
{context_str}

[RAW JOB DESCRIPTION TEXT START]
{request.job_description}
[RAW JOB DESCRIPTION TEXT END]

Extract and return JSON with keys:
"job_title", "company", "required_skills", "preferred_skills", "technologies", "education_requirements", "experience_requirements", "keywords".
"""
    return prompt.strip()


def parse_ai_json_response(raw_response_text: str) -> Dict[str, Any]:
    """Clean markdown code blocks and parse raw JSON output from Gemini."""
    cleaned = raw_response_text.strip()
    # Strip markdown ```json ... ``` code blocks if present
    if cleaned.startswith("```"):
        cleaned = re.sub(r'^```(?:json)?\n?', '', cleaned)
        cleaned = re.sub(r'\n?```$', '', cleaned)

    try:
        return json.loads(cleaned.strip())
    except json.JSONDecodeError as e:
        raise ValueError(f"AI response is not valid JSON: {str(e)}")


def analyze_job_description_service(request: JobAnalyzeRequest) -> JobAnalyzeResponse:
    """
    Main service function to analyze job description using Gemini AI.
    Handles client initialization, prompt execution, output parsing, and safe error handling.
    """
    settings = get_settings()
    api_key = settings.GEMINI_API_KEY

    # Check for API key presence
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gemini AI service is not configured. (GEMINI_API_KEY environment variable missing)",
        )

    try:
        client = genai.Client(api_key=api_key)
        prompt = build_analysis_prompt(request)

        # Call Gemini API
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                temperature=0.1,
            ),
        )

        if not response or not response.text:
            raise ValueError("Gemini API returned an empty response.")

        # Parse JSON payload from AI
        data = parse_ai_json_response(response.text)

        # Fallback to user-provided title/company if AI returned null
        job_title = data.get("job_title") or request.job_title
        company = data.get("company") or request.company

        # Construct and validate Pydantic response
        return JobAnalyzeResponse(
            job_title=job_title,
            company=company,
            required_skills=data.get("required_skills", []),
            preferred_skills=data.get("preferred_skills", []),
            technologies=data.get("technologies", []),
            education_requirements=data.get("education_requirements", []),
            experience_requirements=data.get("experience_requirements", []),
            keywords=data.get("keywords", []),
        )

    except HTTPException as http_ex:
        raise http_ex
    except Exception as ex:
        # Never expose API key or internal credentials in exception detail
        safe_detail = "Failed to analyze job description due to an AI processing or response format error."
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=safe_detail,
        )
