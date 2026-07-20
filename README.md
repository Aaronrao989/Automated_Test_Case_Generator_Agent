<div align="center">

# 🧪 TestCaseAI

**AI-powered test-case generation for Python — analyze code, generate pytest suites, run them, and measure real coverage.**

Next.js · FastAPI · Groq · PostgreSQL — deployable entirely on free tiers.

</div>

---

## Overview

TestCaseAI takes a code snippet, a public GitHub repository, or a ZIP upload,
extracts its functions, identifies edge cases, uses a Groq LLM to generate
comprehensive `pytest` tests, executes them in an isolated environment, and
reports real line coverage — all through a clean, modern web UI.

It is a public demo (no login) designed to run on **Vercel + Render + Supabase**
free tiers with **no Docker, Redis, Celery, or paid infrastructure**.

## Features

- 🤖 **AI test generation** — Groq-powered pytest with happy paths, boundaries, and `pytest.raises`
- 🔍 **Edge-case detection** — null, boundary, type-mismatch, and exception analysis
- ▶️ **Isolated execution** — each job runs in its own temp dir; tests run exactly once
- 📊 **Real coverage** — collected from the same run (not estimated)
- 📈 **Live progress** — staged status (scan → extract → generate → run → coverage) with elapsed time
- 🗂️ **Rich results** — tabs, syntax highlighting, copy, download tests as ZIP, coverage export
- 🌓 **Dark / light mode**, responsive design, loading skeletons, empty/error states
- 🕘 **History** — recent analyses with quick lookup and delete
- 🔒 **Hardened** — SSRF-guarded cloning, zip-slip protection, size-limited uploads, in-memory rate limiting

## Architecture

```
Next.js (Vercel)  →  FastAPI + BackgroundTasks (Render)  →  PostgreSQL (Supabase)
                                  │
                                  └─→ Groq LLM (batched requests)
```

Async work uses FastAPI `BackgroundTasks` in-process. Progress is written to the
job row and polled by the client. See [ARCHITECTURE.md](ARCHITECTURE.md).

## Tech stack

| Layer | Tech |
|---|---|
| Frontend | Next.js 16 (App Router), React 18, TypeScript, Tailwind CSS, lucide-react |
| Backend | FastAPI, SQLAlchemy 2, Pydantic v2, Uvicorn |
| LLM | Groq (`openai/gpt-oss-120b` / `llama-3.1-8b-instant`) |
| Database | PostgreSQL (Supabase or Render); SQLite for local/dev |
| CI | GitHub Actions (pytest + lint + build) |

## Folder structure

```
backend/
  app/
    main.py              FastAPI app, CORS, health, startup reconciliation
    core/                config, in-memory rate limiter
    db/database.py       engine + session
    models/              AnalysisJob (single table, JSON results)
    schemas/             request/response models
    api/                 analysis routes (+ aggregate router)
    services/            background analysis worker
    agents/              orchestrator, repo_scanner, edge_case_finder, llm_test_generator
  tests/                 pytest suite
frontend/
  src/
    app/                 landing, /analyze, /results/[jobId], /dashboard
    components/          nav, footer, theme-toggle, ui/*
    lib/                 api client, types, highlight, zip, utils
```

## Local setup

**Backend**
```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # leave GROQ_API_KEY empty for offline "demo" mode
uvicorn app.main:app --reload    # http://localhost:8000  (docs at /docs)
```

**Frontend**
```bash
cd frontend
npm install
cp .env.example .env.local   # set NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev                  # http://localhost:3000
```

## Environment variables

**Backend** (`backend/.env`): `DATABASE_URL`, `GROQ_API_KEY`, `LLM_PROVIDER`,
`GROQ_MODEL`, `CORS_ORIGINS`, `ENVIRONMENT` (optional: `LLM_BATCH_SIZE`,
`MAX_FILE_SIZE`, `MAX_FUNCTIONS_TO_ANALYZE`).

**Frontend** (`frontend/.env.local`): `NEXT_PUBLIC_API_URL`.

## API

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/v1/analysis/start` | Analyze a snippet or GitHub URL |
| POST | `/api/v1/analysis/upload` | Analyze an uploaded ZIP |
| GET | `/api/v1/analysis` | List recent analyses |
| GET | `/api/v1/analysis/{job_id}` | Poll status/stage/results |
| DELETE | `/api/v1/analysis/{job_id}` | Delete a job |
| GET | `/health` | Health check |

## Deployment

- **Database:** create a Supabase/Render Postgres, copy the pooled URL into `DATABASE_URL`.
- **Backend (Render Web Service):** root `backend/`, build `pip install -r requirements.txt`,
  start `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. Set env vars from `.env.example`.
- **Frontend (Vercel):** root `frontend/`, set `NEXT_PUBLIC_API_URL` to the Render URL,
  then add that Vercel domain to the backend's `CORS_ORIGINS`.

## Screenshots

<!-- Add screenshots of the landing page, analyze flow, and results page here -->
| Landing | Analyze | Results |
|---|---|---|
| _screenshot_ | _screenshot_ | _screenshot_ |

## Tests & evaluation

```bash
cd backend && pytest tests/ -v          # unit + integration tests
cd backend && python -m evals.run_eval  # score the generator on a golden dataset
cd frontend && npm run lint && npm run build
```

The **evaluation harness** (`backend/evals/`) runs the generator against a
golden set of functions and scores it on relevance, generation rate, test
pass-rate, and coverage — and runs in CI on every push. With a `GROQ_API_KEY`
set it reports full pass-rate/coverage; offline it validates the pipeline.

### CI / PR integration

A **CLI** (`python -m app.cli <files> --out report.md`) generates tests for any
Python files and emits a Markdown report. The **`PR Test Generation`** workflow
(`.github/workflows/pr-test-gen.yml`) runs it on a pull request's changed
`.py` files and posts the generated tests + pass-rate + coverage as a PR
comment. Add a `GROQ_API_KEY` repository secret for real LLM output.

## Future scope

- Containerized sandbox for executing arbitrary-dependency repos
- JavaScript/TypeScript test generation & execution
- Mutation testing and coverage heatmaps
- Multi-file dependency resolution
- Optional accounts + persistent per-user history

## License

MIT © Team Osaka Vise — built for the Capgemini Exceller AgentifAI Buildathon.
