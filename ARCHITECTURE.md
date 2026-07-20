# System Architecture

## Overview

A two-tier application deployable entirely on free tiers:

- **Frontend** — Next.js (App Router) SPA on Vercel.
- **Backend** — FastAPI on a single Render Web Service. Long-running work runs
  via FastAPI `BackgroundTasks` (same process, no external worker).
- **Database** — PostgreSQL (Supabase or Render). SQLite for local/dev.
- **LLM** — Groq. Requests are batched to reduce API calls and rate-limit pressure.

No Docker, Redis, Celery, broker, or long-running worker. This is a public demo
with **no authentication**.

## Agentic design

The `TestGenerationOrchestrator` acts as an **agent** that invokes a fixed
catalog of **tools** — `scan_repository`, `extract_functions`,
`detect_edge_cases`, `generate_tests`, `execute_tests`, `compute_coverage`
(see `agents/agent_trace.py`). Every run records a **tool-call trace** (name,
description, status, duration, result summary) which is returned in the API
response (`agent_trace`, `tools`) and rendered as a timeline in the UI. This
makes the pipeline observable and explainable rather than a black box.

## Request lifecycle

```
Browser (/analyze)
  │  POST /api/v1/analysis/start   (or /upload for a ZIP; rate-limited)
  ▼
FastAPI route
  │  create AnalysisJob(PENDING) → 202 {job_id} → schedule BackgroundTask
  ▼
run_analysis (background, same process)
  │  status → IN_PROGRESS, writes job.results = {"stage": ...} per step
  ▼
TestGenerationOrchestrator  (inside tempfile.TemporaryDirectory)
  │  scan → extract functions → edge cases → batched LLM →
  │  write test files → run pytest ONCE with --cov → parse results + coverage
  ▼
job.status = COMPLETED, job.results = {structure, stats, edge_cases, tests, ...}
  ▲
  │  GET /api/v1/analysis/{job_id}  ← client polls; sees stage, then results
Browser (/results/[jobId]) renders tabs + coverage + downloads
```

## Progress reporting

The orchestrator calls an `on_stage` callback at each step; the worker writes
the stage into `job.results` and commits. `GET /{job_id}` returns the current
stage while `IN_PROGRESS`, so the frontend shows a live stepper with elapsed time
— all over simple polling, no websockets.

## Isolation & concurrency

Every job executes in its own `tempfile.TemporaryDirectory`, so concurrent jobs
never share files and scratch state is auto-cleaned. Tests run exactly once;
coverage is derived from that same run (`coverage.executed` distinguishes
"0% because nothing ran" from genuine 0%).

## Groq usage

Functions are grouped into batches (`LLM_BATCH_SIZE`, default 3) and generated in
a single request using a `### FUNCTION: <name>` delimiter, cutting API calls by
~3×. Rate limits are handled with exponential backoff + jitter; on failure the
pipeline degrades to a deterministic demo test per function rather than erroring.

## Failure handling

Free-tier hosts spin down when idle and on deploy, killing in-flight
`BackgroundTasks`. `reconcile_stuck_jobs()` runs at startup and marks any
`PENDING`/`IN_PROGRESS` jobs as `FAILED` so they don't hang.

## Security

- In-process fixed-window **rate limiter** (no Redis) protects the Groq quota.
- **SSRF:** repo URLs restricted to an allow-list of git hosts over https;
  `GIT_ALLOW_PROTOCOL=https` blocks `file://`/`ssh://`.
- **Path traversal:** ZIP extraction skips `..`/absolute members; uploads are
  size-capped and streamed.
- A global exception handler logs server-side and returns generic messages.

> **Known limitation:** executed code runs in a subprocess with a timeout, not a
> container sandbox. Coverage/execution is reliable for self-contained,
> standard-library code; repos with third-party imports won't execute in the
> runner (surfaced to the user as a clear notice).

## Data model

A single `analysis_jobs` table stores status plus the full analysis output as a
JSON document — trivial to operate on a free Postgres tier and easy to query by
job id.
