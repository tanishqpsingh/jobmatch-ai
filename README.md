# JobMatch AI 🎯

JobMatch AI is an intelligent full-stack web application designed to help job seekers analyze resumes against job descriptions, calculate explainable match compatibility, identify skill gaps, generate tailored recommendations, organize job applications, and accelerate career preparation using Gemini AI.

---

## 🚀 Project Vision & Core Features

- **Resume Intelligence & Parsing**: Extract structured information (Name, Email, Phone, Education, Skills, Experience, Projects, Certifications) from PDF and DOCX resumes using high-precision parsers (`PyMuPDF`, `python-docx`).
- **Job Description Intelligence**: Analyze job postings using Google Gemini AI to extract required/preferred skills, technologies, education, experience, and domain keywords.
- **Explainable Resume ↔ Job Matching**: Deterministically compare candidate qualifications against job requirements without artificial percentage guesswork.
- **Application Tracking System**: Track job applications, application statuses (`saved`, `applied`, `screening`, `interview`, `offer`, `rejected`, `withdrawn`), scheduled interview dates, and notes in a centralized database dashboard.
- **AI Career Assistant & Growth Toolkit**:
  - **Resume Bullet Improver**: Enhance bullet point impact without inventing metrics or achievements.
  - **Missing Skill Explainer**: Get plain-language explanations and beginner learning roadmaps for missing competencies.
  - **Interview Question Generator**: Generate technical, behavioral, and role-specific practice questions.
  - **Job Interview Prep Guide**: Receive revision topics, technical focus areas, and practice strategies.
  - **Technology Explainer**: Understand specific technologies and their relevance to target roles.
  - **Study Plan Generator**: Build week-by-week learning roadmaps to master missing skills.

---

## 🛠️ Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend** | [Next.js](https://nextjs.org/) (App Router), [React](https://react.dev/), [TypeScript](https://www.typescriptlang.org/), [Tailwind CSS](https://tailwindcss.com/) |
| **Backend** | [Python 3.11+](https://www.python.org/), [FastAPI](https://fastapi.tiangolo.com/), [Pydantic v2](https://docs.pydantic.dev/), [Uvicorn](https://www.uvicorn.org/) |
| **Database** | [PostgreSQL 16](https://www.postgresql.org/), [SQLAlchemy ORM](https://www.sqlalchemy.org/), [asyncpg](https://github.com/MagicStack/asyncpg), [SQLite](https://www.sqlite.org/) (Isolated Test Engine) |
| **AI Engine** | [Google Gemini API](https://ai.google.dev/) (`google-genai`) |
| **Document Processing**| [PyMuPDF](https://pymupdf.readthedocs.io/), [python-docx](https://python-docx.readthedocs.io/) |
| **Testing** | [pytest](https://docs.pytest.org/), [HTTPX](https://www.python-httpx.org/) (backend), [Playwright](https://playwright.dev/) (frontend, planned) |
| **DevOps & Containers** | [Docker Compose](https://docs.docker.com/compose/) |

---

## 📍 Current Phase: Phase 6 — AI Career Assistant

**Status:** Completed & Verified ✅

### Completed Capabilities in Phase 6
- **Strict Factual Integrity Safeguards**:
  - AI system prompts strictly prohibit inventing work experience, achievements, metrics, degrees, or certifications.
  - Candidate inputs are isolated from system instructions to defend against prompt injection attempts.
- **Full AI Career Assistant API Suite**:
  - `POST /api/v1/career/improve-bullet` — Enhances bullet points while preserving factual scope.
  - `POST /api/v1/career/explain-skill` — Explains missing skills and beginner project ideas.
  - `POST /api/v1/career/interview-questions` — Generates categorized interview practice questions.
  - `POST /api/v1/career/interview-prep` — Builds job-specific revision topics and focus strategies.
  - `POST /api/v1/career/explain-technology` — Plain-language tech explanations with starter exercises.
  - `POST /api/v1/career/study-plan` — Generates week-by-week learning roadmaps.
- **Mocked Test Suite**: All 55 backend `pytest` tests run with zero external network dependency using `unittest.mock`.
- **Interactive Next.js UI Component**: [`CareerAssistant.tsx`](file:///c:/Users/tanis/jobmatch-ai/frontend/src/components/CareerAssistant.tsx) rendering dedicated sub-tools, loading states, error alerts, and formatted output cards.

---

## 📂 Project Structure

```
jobmatch-ai/
├── backend/                  # FastAPI backend application
│   ├── app/
│   │   ├── __init__.py       # App package initializer
│   │   ├── config.py         # Pydantic Settings & environment config
│   │   ├── main.py           # FastAPI entry point & routes (/health, /api/v1/*)
│   │   ├── db/
│   │   │   ├── database.py   # SQLAlchemy engine, sessionmaker, & init_db()
│   │   │   └── models.py     # Application SQLAlchemy ORM model
│   │   ├── routers/
│   │   │   ├── resumes.py    # POST /api/v1/resumes/parse router
│   │   │   ├── jobs.py       # POST /api/v1/jobs/analyze router
│   │   │   ├── matching.py   # POST /api/v1/matching/analyze router
│   │   │   ├── applications.py # Application CRUD & summary endpoints
│   │   │   └── career.py     # AI Career Assistant endpoints
│   │   ├── schemas/
│   │   │   ├── resume.py     # Pydantic schema for parsed resume output
│   │   │   ├── job.py        # Pydantic schema for job analysis
│   │   │   ├── matching.py   # Pydantic schema for matching engine
│   │   │   ├── application.py# Pydantic schema for application tracker & summary
│   │   │   └── career.py     # Pydantic schemas for AI Career Assistant tools
│   │   └── services/
│   │       ├── file_validation.py # File sanitization & magic byte checks
│   │       ├── resume_parser.py   # PyMuPDF & python-docx extraction logic
│   │       ├── job_analyzer.py    # Gemini AI job description analysis service
│   │       ├── matching_engine.py # Deterministic resume/job matching engine
│   │       ├── application_service.py # CRUD & database aggregation service
│   │       └── career_service.py # AI Career Assistant tool services
│   └── requirements.txt      # Python dependencies
├── frontend/                 # Next.js frontend application
│   ├── src/
│   │   ├── app/              # App router pages & layouts
│   │   └── components/
│   │       ├── ResumeUpload.tsx # Drag-and-drop resume parser component
│   │       ├── JobAnalyzer.tsx  # Job description AI analyzer component
│   │       ├── MatchAnalyzer.tsx# Resume to job matching breakdown component
│   │       ├── ApplicationTracker.tsx # Job application tracker & dashboard component
│   │       └── CareerAssistant.tsx # AI Career Assistant toolkit component
│   ├── package.json
│   ├── tsconfig.json
│   └── tailwind.config.ts
├── tests/                    # Backend test suite
│   ├── __init__.py
│   ├── test_health.py        # Health endpoint test
│   ├── test_resume_parser.py # PDF/DOCX parsing & security validation test suite
│   ├── test_job_analyzer.py  # Gemini AI job description analyzer test suite
│   ├── test_matching_engine.py # Deterministic matching engine test suite
│   ├── test_application_tracker.py # Database CRUD & tracker test suite
│   └── test_career_assistant.py # AI Career Assistant tools test suite (mocked Gemini)
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore configuration
├── docker-compose.yml        # PostgreSQL service definition
└── README.md                 # Project documentation
```

---

## 🏁 Getting Started

### Prerequisites

- **Node.js** (v18+ or v20+) and **npm**
- **Python** (v3.10+)
- **Docker** & **Docker Compose** (for PostgreSQL)

---

### 1. Configure Environment Variables

Copy the example environment configuration:

```bash
cp .env.example .env
```

---

### 2. Run PostgreSQL via Docker Compose

Start the PostgreSQL database service in the background:

```bash
docker compose up -d postgres
```

---

### 3. Start the Backend (FastAPI)

1. Create and activate a Python virtual environment:
   ```bash
   # Windows (PowerShell)
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

   # macOS / Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install backend dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```

3. Run the development server:
   ```bash
   uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. Verify backend endpoints:
   - Health check: `GET http://localhost:8000/health`
   - Resume Parsing API: `POST http://localhost:8000/api/v1/resumes/parse`
   - Job Analysis API: `POST http://localhost:8000/api/v1/jobs/analyze`
   - Match Analysis API: `POST http://localhost:8000/api/v1/matching/analyze`
   - Application Tracker API: `GET/POST/PATCH/DELETE http://localhost:8000/api/v1/applications`
   - AI Career Assistant API: `POST http://localhost:8000/api/v1/career/*`
   - Interactive OpenAPI Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### 4. Run Backend Tests

Run the complete test suite with `pytest`:

```bash
# Quiet mode
.\.venv\Scripts\pytest -q

# Verbose mode
.\.venv\Scripts\pytest tests/ -v
```

---

### 5. Start the Frontend (Next.js)

1. Navigate to the `frontend/` directory and install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start the local development server:
   ```bash
   npm run dev
   ```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

4. To build for production:
   ```bash
   npm run build
   ```

---

## 🔒 Security & Best Practices

- **Zero Secret Commits**: Real API keys and credentials are never stored in source code.
- **Factual Integrity Shield**: System instructions enforce strict factual boundaries to prevent generating fake resume metrics or unsupplied experience.
- **Prompt Injection Defense**: Untrusted text from resumes or job postings is isolated in dedicated user content blocks.
- **Safe Error Handling**: AI errors return clean HTTP status codes without leaking API keys or internal stack traces.
- **Mocked Automated Testing**: Test suite uses `unittest.mock` to simulate AI calls without requiring external network calls or active API keys.
- **AI Disclaimer**: AI-generated recommendations are educational suggestions; factual candidate information originates solely from user-supplied documents.
