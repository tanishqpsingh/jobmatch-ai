import re
from typing import List, Tuple, Set
from google import genai
from google.genai import types
from backend.app.config import get_settings
from backend.app.schemas.matching import (
    CompatibilityAnalysis,
    CompatibilityStatus,
    MatchAnalyzeRequest,
    MatchAnalyzeResponse,
)

settings = get_settings()


def normalize_string(text: str) -> str:
    """Normalize string by converting to lowercase and trimming whitespace."""
    if not text:
        return ""
    return text.strip().lower()


def is_token_in_text(token: str, text: str) -> bool:
    """
    Check if token exists in text using word boundaries to avoid false positives.
    E.g. 'Java' will NOT match inside 'JavaScript', 'C' will NOT match inside 'CSS'.
    """
    norm_token = normalize_string(token)
    norm_text = normalize_string(text)

    if not norm_token or not norm_text:
        return False

    # For special single/double char tokens like C++, C#, .NET, R, handle regex escape
    pattern = r'(?:\b|_)' + re.escape(norm_token) + r'(?:\b|_)'
    return bool(re.search(pattern, norm_text))


def match_items(job_items: List[str], candidate_text_corpus: str, candidate_items: List[str]) -> Tuple[List[str], List[str]]:
    """
    Compare a list of job requirement items against candidate text corpus and candidate items.
    Returns (matching_items, missing_items).
    """
    matching: List[str] = []
    missing: List[str] = []

    # Normalized candidate items pool for direct item comparison
    candidate_items_norm = {normalize_string(item) for item in candidate_items if item and item.strip()}

    seen = set()
    for item in job_items:
        clean_item = item.strip()
        if not clean_item:
            continue

        norm_item = normalize_string(clean_item)
        if norm_item in seen:
            continue
        seen.add(norm_item)

        # Check direct item match OR word-boundary regex search in corpus
        is_match = (norm_item in candidate_items_norm) or is_token_in_text(clean_item, candidate_text_corpus)

        if is_match:
            matching.append(clean_item)
        else:
            missing.append(clean_item)

    return matching, missing


def evaluate_education(resume_edu: List[str], job_edu: List[str], resume_raw_text: str) -> CompatibilityAnalysis:
    """Evaluate education requirements against candidate education deterministically."""
    if not job_edu:
        return CompatibilityAnalysis(
            status="insufficient_information",
            details="No explicit education requirements were specified in the job posting.",
        )

    if not resume_edu and not is_token_in_text("degree", resume_raw_text) and not is_token_in_text("bachelor", resume_raw_text):
        return CompatibilityAnalysis(
            status="insufficient_information",
            details="The resume does not explicitly state education or degree details.",
        )

    degree_levels = {
        "doctorate": 4, "phd": 4, "ph.d": 4,
        "master": 3, "ms": 3, "m.s": 3, "mba": 3, "m.b.a": 3,
        "bachelor": 2, "bs": 2, "b.s": 2, "ba": 2, "b.a": 2,
        "associate": 1
    }

    job_text = " ".join(job_edu).lower()
    resume_text = (" ".join(resume_edu) + " " + resume_raw_text).lower()

    # Find required degree level
    required_level = 0
    for title, level in degree_levels.items():
        if is_token_in_text(title, job_text):
            required_level = max(required_level, level)

    # Find candidate degree level
    candidate_level = 0
    for title, level in degree_levels.items():
        if is_token_in_text(title, resume_text):
            candidate_level = max(candidate_level, level)

    if required_level == 0 and candidate_level == 0:
        return CompatibilityAnalysis(
            status="insufficient_information",
            details="Education details were found, but specific degree levels could not be compared.",
        )

    if candidate_level >= required_level:
        return CompatibilityAnalysis(
            status="match",
            details=f"Candidate education meets or exceeds the required qualification level.",
        )
    elif candidate_level > 0:
        return CompatibilityAnalysis(
            status="partial_match",
            details="Candidate possesses higher education, but it may be lower than the preferred degree level.",
        )
    else:
        return CompatibilityAnalysis(
            status="mismatch",
            details="Candidate does not appear to list the required degree level.",
        )


def evaluate_experience(resume_exp: List[str], job_exp: List[str], resume_raw_text: str) -> CompatibilityAnalysis:
    """Evaluate work experience requirements deterministically."""
    if not job_exp:
        return CompatibilityAnalysis(
            status="insufficient_information",
            details="No explicit experience requirements were specified in the job posting.",
        )

    if not resume_exp and len(resume_raw_text) < 100:
        return CompatibilityAnalysis(
            status="insufficient_information",
            details="The resume provides insufficient experience records for verification.",
        )

    job_exp_text = " ".join(job_exp)

    # Extract required years of experience from job requirements
    years_match = re.search(r'(\d+)\+?\s*(?:-\s*\d+\s*)?years?', job_exp_text, re.IGNORECASE)
    required_years = int(years_match.group(1)) if years_match else None

    # Check candidate work experience count / items
    if not resume_exp:
        return CompatibilityAnalysis(
            status="insufficient_information",
            details="Candidate lists experience details, but numerical years of experience could not be verified automatically.",
        )

    exp_count = len(resume_exp)

    if required_years is not None:
        if exp_count >= required_years or (required_years <= 3 and exp_count >= 1):
            return CompatibilityAnalysis(
                status="match",
                details=f"Candidate provides {exp_count} experience record(s), aligning with the required {required_years}+ years.",
            )
        else:
            return CompatibilityAnalysis(
                status="partial_match",
                details=f"Candidate lists {exp_count} experience entry/entries, which may be below the target {required_years} years.",
            )

    return CompatibilityAnalysis(
        status="match" if exp_count >= 1 else "insufficient_information",
        details=f"Candidate lists {exp_count} relevant experience role(s).",
    )


def generate_deterministic_summary(
    match_req: List[str],
    miss_req: List[str],
    match_tech: List[str],
    edu_status: str,
    exp_status: str,
) -> str:
    """Synthesize a human-readable, explainable summary from deterministic findings."""
    total_req = len(match_req) + len(miss_req)
    req_coverage = f"{len(match_req)}/{total_req}" if total_req > 0 else "N/A"

    parts = [
        f"Skill Coverage: Candidate matches {req_coverage} required skills.",
    ]

    if match_req:
        parts.append(f"Key Matching Strengths: {', '.join(match_req[:5])}.")

    if miss_req:
        parts.append(f"Missing Required Skills: {', '.join(miss_req[:5])}.")

    parts.append(f"Education Compatibility: {edu_status.replace('_', ' ').title()}.")
    parts.append(f"Experience Compatibility: {exp_status.replace('_', ' ').title()}.")

    return " ".join(parts)


def compute_match(request: MatchAnalyzeRequest) -> MatchAnalyzeResponse:
    """
    Main service entry point for matching a parsed resume against an analyzed job description.
    Uses deterministic matching engine as source of truth.
    """
    resume = request.resume
    job = request.job

    # Build comprehensive text corpus for candidate
    candidate_corpus_parts = [
        resume.raw_text,
        " ".join(resume.skills),
        " ".join(resume.education),
        " ".join(resume.experience),
        " ".join(resume.projects),
        " ".join(resume.certifications),
    ]
    candidate_corpus = "\n".join(candidate_corpus_parts)

    # 1. Required Skills Match
    matching_skills, missing_required_skills = match_items(
        job.required_skills, candidate_corpus, resume.skills
    )

    # 2. Preferred Skills Match
    _, missing_preferred_skills = match_items(
        job.preferred_skills, candidate_corpus, resume.skills
    )

    # 3. Technologies Match
    matching_technologies, missing_technologies = match_items(
        job.technologies, candidate_corpus, resume.skills
    )

    # 4. Keywords Match
    matching_keywords, missing_keywords = match_items(
        job.keywords, candidate_corpus, resume.skills
    )

    # 5. Education Analysis
    edu_analysis = evaluate_education(resume.education, job.education_requirements, resume.raw_text)

    # 6. Experience Analysis
    exp_analysis = evaluate_experience(resume.experience, job.experience_requirements, resume.raw_text)

    # 7. Summary Generation (Deterministic Base)
    summary = generate_deterministic_summary(
        matching_skills,
        missing_required_skills,
        matching_technologies,
        edu_analysis.status,
        exp_analysis.status,
    )

    # 8. Optional Gemini AI Summary Refinement
    current_settings = get_settings()
    if current_settings.GEMINI_API_KEY:
        try:
            client = genai.Client(api_key=current_settings.GEMINI_API_KEY)
            ai_prompt = f"""
Summarize the following deterministic resume-to-job comparison results in 2-3 objective sentences.
Do NOT invent qualifications or change the data provided.

[DETERMINISTIC DATA]
Job Title: {job.job_title}
Matching Skills: {', '.join(matching_skills) if matching_skills else 'None'}
Missing Required Skills: {', '.join(missing_required_skills) if missing_required_skills else 'None'}
Education Status: {edu_analysis.status}
Experience Status: {exp_analysis.status}
"""
            response = client.models.generate_content(
                model=current_settings.GEMINI_MODEL,
                contents=ai_prompt,
                config=types.GenerateContentConfig(temperature=0.2),
            )
            if response and response.text:
                summary = response.text.strip()
        except Exception:
            # Fall back seamlessly to deterministic summary if AI call fails
            pass

    return MatchAnalyzeResponse(
        matching_skills=matching_skills,
        missing_required_skills=missing_required_skills,
        missing_preferred_skills=missing_preferred_skills,
        matching_technologies=matching_technologies,
        missing_technologies=missing_technologies,
        education_analysis=edu_analysis,
        experience_analysis=exp_analysis,
        matching_keywords=matching_keywords,
        missing_keywords=missing_keywords,
        summary=summary,
    )
