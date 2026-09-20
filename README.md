# JobMatch AI

JobMatch AI is a production-grade, full-stack career acceleration platform that analyzes resumes against job descriptions, calculates explainable skill compatibility, identifies gaps, tracks job applications, and accelerates interview preparation using Google Gemini AI.

---

## Live Demo

> **Live Production URL:** [Open JobMatch AI](https://extraordinary-caring-production-a1a3.up.railway.app)
>
> **API Health Probe:** [Check API Health](https://jobmatch-ai-production-da1f.up.railway.app/health)

---

## Architecture

```
                 +-----------------------+
                 |   Next.js Frontend    |
                 |  (React, TypeScript,  |
                 |     Tailwind CSS)     |
                 +-----------+-----------+
                             |
                     HTTP / REST APIs
                     (HttpOnly Cookies)
                             |
                             v
                 +-----------------------+
                 |    FastAPI Backend    |
                 |  (Uvicorn ASGI, Pydantic|
                 |   Argon2 & JWT Auth)  |
                 +-----+-----------+-----+
                       |           |
     SQLAlchemy / Psycopg2         Google GenAI SDK
                       |           |
                       v           v
           +---------------+   +-------------------+
           |  PostgreSQL   |   | Google Gemini API |
           |  (Migrations  |   | (Structured JSON, |
           |  via Alembic) |   |  Anti-Injection)  |
           +---------------+   +-------------------+
```

---

## Features

- **Resume Intelligence & Parsing**: High-precision in-memory text extraction for `.pdf` and `.docx` files using `PyMuPDF` and `python-docx`, validating magic bytes, MIME types, and file structure without persisting candidate files to disk.
- **Job Description Intelligence**: Extracts required/preferred technical skills, technologies, education, experience, and domain keywords with strict JSON schema compliance powered by Google Gemini.
- **Explainable Match Engine**: Computes deterministic compatibility metrics across skills, technologies, education, and experience without arbitrary percentage guesswork.
- **Application Tracking System (ATS)**: Multi-status pipeline tracker (`saved`, `applied`, `screening`, `interview`, `offer`, `rejected`, `withdrawn`) with interview scheduling and notes, isolated per user.
- **AI Career Assistant & Growth Toolkit**:
  - *Resume Bullet Improver*: Enhances bullet points while strictly prohibiting invented metrics, credentials, or companies.
  - *Missing Skill Explainer*: Provides plain-English explanations and beginner projects for identified skill gaps.
  - *Interview Question Generator*: Categorizes technical, behavioral, and role-specific practice questions with evaluation criteria.
  - *Interview Prep Guide*: Generates customized focus topics and revision strategies.
  - *Technology Explainer*: Breaks down enterprise technologies and their relevance to target roles.
  - *Study Plan Generator*: Builds week-by-week learning roadmaps.
- **User Authentication & Isolation**: Secure registration, login, logout, and token refresh with Argon2 password hashing and HttpOnly cookie management.

---

## Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend** | Next.js (App Router, Standalone), React 19, TypeScript, Tailwind CSS |
| **Backend** | Python 3.11, FastAPI, Uvicorn, Pydantic v2 |
| **Database & ORM** | PostgreSQL, SQLAlchemy 2.0, Psycopg2-binary, Alembic, SQLite (dev/test fallback) |
| **AI Integration** | Google Gemini API (`google-genai`), Gemini 2.5 Flash |
| **Document Processing** | PyMuPDF (fitz), python-docx |
| **Testing** | pytest, pytest-asyncio, HTTPX TestClient |
| **DevOps & Hosting** | Docker (Multi-stage builds), Railway |

---

## Authentication

JobMatch AI implements a dual-mode authentication system:

1. **Browser Clients (Production)**:
   - Tokens are issued inside **HttpOnly**, `Secure` (in production), `SameSite` cookies (`access_token` and `refresh_token`).
   - JavaScript running in the browser cannot read or exfiltrate tokens via XSS.
2. **API & Test Clients (Bearer Fallback)**:
   - Endpoints accept standard `Authorization: Bearer <token>` headers, enabling programmatic access and zero-friction automated testing.
3. **Password Security**:
   - Passwords are salted and hashed using **Argon2** via `passlib`, protecting user credentials against brute-force and dictionary attacks.
4. **Data Isolation**:
   - All application tracker endpoints enforce row-level tenant ownership (`current_user.id`), ensuring candidates can only view and modify their own data.

---

## Testing

The backend is backed by an automated test suite executed via `pytest`. All tests use isolated in-memory SQLite fixtures and mocked AI responses, requiring zero external network calls or API keys.

- **Test Suite Status**: **75 passed** (100% passing)
- **Coverage Areas**:
  - Resume file validation, MIME spoofing, magic bytes, and parsing
  - Job description parsing and JSON schema extraction
  - Resume-to-job matching algorithms and edge cases
  - Application CRUD, summary aggregation, and tenant isolation
  - Career assistant tools, prompt isolation, and factual integrity validation
  - Liveness (`/health`), readiness (`/health/ready`), and root service metadata

---

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 20+ and npm
- (Optional) PostgreSQL 16 or Docker

### 1. Clone Repository
```bash
git clone https://github.com/tanishqpsingh/jobmatch-ai.git
cd jobmatch-ai
```

### 2. Backend Setup
```bash
# Create and activate Python virtual environment
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and supply your GEMINI_API_KEY (obtainable from https://aistudio.google.com/)

# Run database migrations
alembic upgrade head

# Start FastAPI server
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000` to interact with the application.

---

## Production Deployment (Railway)

The application is deployed across three linked services within a single Railway project:

1. **PostgreSQL Service**: Managed PostgreSQL database.
2. **Backend Service** (FastAPI):
   - **Build**: Dockerfile (`backend/Dockerfile`)
   - **Start Command**: `./start.sh` (executes `alembic upgrade head` before binding to `$PORT`)
   - **Environment Variables**:
     - `ENVIRONMENT=production`
     - `DATABASE_URL=${{Postgres.DATABASE_URL}}`
     - `GEMINI_API_KEY=<your-production-gemini-key>`
     - `JWT_SECRET=<random-64-character-secret>`
     - `CORS_ORIGINS=https://<your-frontend>.up.railway.app`
3. **Frontend Service** (Next.js):
   - **Build**: Dockerfile (`frontend/Dockerfile`)
   - **Environment Variables**:
     - `NEXT_PUBLIC_API_URL=https://<your-backend>.up.railway.app`

---

## Environment Variables

| Variable | Description | Required In |
| :--- | :--- | :--- |
| `ENVIRONMENT` | Runtime environment (`development` or `production`) | Backend |
| `DATABASE_URL` | PostgreSQL connection URI (`postgresql://...`) | Backend |
| `GEMINI_API_KEY` | Google Gemini API credential for AI analysis | Backend |
| `JWT_SECRET` | Cryptographic secret for signing authentication tokens | Backend |
| `CORS_ORIGINS` | Comma-separated list of allowed frontend origins | Backend |
| `COOKIE_SAMESITE` | SameSite cookie policy (`lax` or `none`) | Backend |
| `NEXT_PUBLIC_API_URL`| Public URL of the FastAPI backend service | Frontend |

---

## Security Review

| Category | Control Implemented | Severity Addressed |
| :--- | :--- | :--- |
| **Authentication** | Argon2 password hashing; short-lived JWT access tokens + refresh tokens | Critical |
| **Cookie Security** | HttpOnly, HTTPS-enforced `Secure` flag in production, configurable `SameSite` | High |
| **CORS Policy** | Explicit origin whitelist via `CORS_ORIGINS`; wildcards disallowed with credentials | High |
| **File Uploads** | Magic-byte checking, MIME type allowlists, 5MB ceiling, in-memory stream processing | High |
| **Prompt Injection** | Candidate text strictly separated into user payload; system prompt forbids hallucination | High |
| **Database Migrations**| Zero-data-loss Alembic migrations with runtime orphaned-row abort checks | Medium |
| **Surface Hardening** | Interactive OpenAPI `/docs` and `/redoc` automatically disabled in production | Low |

---

## Project Structure

```
jobmatch-ai/
├── backend/
│   ├── alembic/              # Alembic migration environment and versions
│   │   └── versions/         # Schema migration scripts (users & applications)
│   ├── app/
│   │   ├── db/               # SQLAlchemy engine, session maker, and ORM models
│   │   ├── routers/          # API route handlers (auth, resumes, jobs, matching, etc.)
│   │   ├── schemas/          # Pydantic validation models
│   │   ├── services/         # Business logic, Gemini integration, and file parsing
│   │   ├── config.py         # Application settings via pydantic-settings
│   │   ├── dependencies.py   # Token decoding, auth dependency, password hashing
│   │   └── main.py           # FastAPI application entry point, CORS, health probes
│   ├── Dockerfile            # Production Python container specification
│   ├── requirements.txt      # Backend Python dependencies
│   └── start.sh              # Container startup script (migrations + uvicorn)
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js App Router (layout.tsx, page.tsx)
│   │   ├── components/       # UI components (Upload, Analyzer, Tracker, Assistant, Auth)
│   │   └── lib/              # Centralized API utilities and URL builders
│   ├── Dockerfile            # Production Next.js multi-stage container specification
│   ├── next.config.ts        # Next.js configuration (output: standalone)
│   ├── package.json          # Frontend dependencies and scripts
│   └── tsconfig.json         # TypeScript configuration
├── tests/                    # 75 automated pytest unit and integration tests
├── .env.example              # Safe environment variable templates
├── alembic.ini               # Alembic migration configuration
├── docker-compose.yml        # Local PostgreSQL container service
├── railway.json              # Railway project deployment configuration
└── README.md                 # Project documentation and portfolio presentation
```

---

## Portfolio Notes

- **Backend Engineering**: Clean separation of concerns across API routers, Pydantic schemas, and modular service layers. Dynamic ASGI startup conforms to cloud-native platforms.
- **Frontend Engineering**: Built on Next.js 16 App Router using React 19 and Tailwind CSS. Utilizes standalone build output for lightweight production container images.
- **AI System Design**: Grounded Gemini 2.5 Flash prompt engineering prevents hallucinations and maintains strict factual integrity across resume improvements.
- **Database Architecture**: Resilient database lifecycle using SQLAlchemy 2.0 and Alembic. Safe schema migrations prevent catastrophic data loss on existing records.
- **Security Engineering**: Defense-in-depth model featuring Argon2 password hashing, HttpOnly cookie authentication, strict CORS origins, and file validation.
- **Testing & Quality Assurance**: 75 comprehensive tests covering all critical paths with zero network dependencies.
