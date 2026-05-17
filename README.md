# 🧪 Automated Test Case Generator Agent

> **Capgemini Exceller AgentifAI Buildathon** · Team **Osaka Vise**

[![Live App](https://img.shields.io/badge/Live%20App-Vercel-black?style=flat-square&logo=vercel)](https://automatedtestcasegeneratoragent.vercel.app/)
[![API Docs](https://img.shields.io/badge/API%20Docs-FastAPI-009688?style=flat-square&logo=fastapi)](https://automated-test-case-generator-agent.onrender.com/docs)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](LICENSE)
[![CI](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?style=flat-square&logo=githubactions)](https://github.com/Aaronrao989/Automated_Test_Case_Generator_Agent/actions)

---

## 🎯 Problem Statement

> Teams lack sufficient tests, causing regressions. Build an agent that generates unit/integration test cases from code or user stories.

This agent analyzes source code repositories and code snippets to **automatically generate, execute, and report on test cases** — solving the test-coverage gap without manual effort.

---

## ✨ Features

| Capability | Description |
|---|---|
| 🤖 AI Test Generation | Groq LLM generates pytest-ready test cases from any Python code |
| 🔍 Edge Case Detection | Identifies boundary conditions, null inputs, type errors, and more |
| 📦 Repository Analysis | Scans entire repos or ZIP uploads and extracts all testable functions |
| ▶️ Automatic Execution | Runs generated tests via pytest and captures pass/fail results |
| 📊 Coverage Reporting | Computes and visualizes code coverage metrics |
| 🔄 CI Integration | GitHub Actions pipeline for automated testing on every push |
| 🌐 Interactive Dashboard | Real-time job status, test viewer, and execution logs |
| 🌍 Multi-language Detection | Identifies languages and project structure automatically |

---

## 🏗️ Architecture

```
Frontend (Next.js + Vercel)
        ↓
FastAPI Backend (Render)
        ↓
BackgroundTasks (async, no Celery/Redis)
        ↓
Groq LLM (llama-3.1-8b-instant)
        ↓
PostgreSQL (Render)
```

### AI Pipeline

```
Input (Repo / Code Snippet)
        ↓
  Repository Scanner
        ↓
  Function Extraction
        ↓
  Edge Case Detection
        ↓
  LLM Test Generation
        ↓
    Pytest Execution
        ↓
  Coverage Analysis
        ↓
  Dashboard Reporting
```

---

## 🛠️ Tech Stack

**Backend** · FastAPI · SQLAlchemy · PostgreSQL · Groq API · Pytest · Python 3.11 · BackgroundTasks

**Frontend** · Next.js 16 · TypeScript · TailwindCSS · Lucide React

**Deployment** · Vercel (Frontend) · Render (Backend + PostgreSQL) · GitHub Actions (CI/CD)

---

## 📡 API Reference

### `POST /api/v1/analysis/start`
Start analysis on a code snippet or repository.

```json
{
  "source_type": "code_snippet",
  "source_data": "def add(a, b): return a + b"
}
```

### `POST /api/v1/analysis/upload`
Upload a ZIP archive of your repository for full project analysis.

### `GET /api/v1/analysis/{job_id}`
Poll for results — returns generated tests, execution logs, and coverage metrics.

### `GET /health`
Health check endpoint.

---

## 🧪 Example Output

Given:
```python
def divide(a, b):
    return a / b
```

The agent generates:
- ✅ Happy path tests
- ✅ Zero division tests
- ✅ Invalid type tests
- ✅ Boundary tests
- ✅ Negative number tests

---

## 📂 Project Structure

```
Automated_Test_Case_Generator_Agent/
├── backend/
│   └── app/
│       ├── agents/
│       │   ├── orchestrator.py
│       │   ├── llm_test_generator.py
│       │   ├── edge_case_finder.py
│       │   ├── repo_scanner.py
│       │   ├── coverage.py
│       │   ├── test_executor.py
│       │   └── code_understanding.py
│       ├── api/
│       ├── core/
│       ├── db/
│       ├── models/
│       ├── schemas/
│       └── main.py
├── frontend/
│   └── src/app/
│       ├── upload/
│       ├── dashboard/
│       ├── tests/
│       └── page.tsx
└── .github/workflows/ci.yml
```

---

## 🚀 Local Setup

### Backend

```bash
git clone https://github.com/Aaronrao989/Automated_Test_Case_Generator_Agent.git
cd Automated_Test_Case_Generator_Agent/backend

python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

pip install -r requirements.txt
uvicorn app.main:app --reload
# → http://localhost:8000
```

### Frontend

```bash
cd ../frontend
npm install
npm run dev
# → http://localhost:3000
```

### Environment Variables

**Backend** (`.env`):
```env
DATABASE_URL=postgresql://...
GROQ_API_KEY=your_groq_key
LLM_PROVIDER=groq
GROQ_MODEL=llama-3.1-8b-instant
```

**Frontend** (`.env.local`):
```env
NEXT_PUBLIC_API_URL=https://automated-test-case-generator-agent.onrender.com
```

---

## 🔄 CI/CD

GitHub Actions runs on every push:
- Backend test suite (`pytest tests/ -v`)
- Frontend lint + build verification
- Coverage checks

---

## 📈 Evaluation Criteria — How We Address Each

| Criterion | Implementation |
|---|---|
| **Test relevance & coverage** | LLM generates context-aware tests with pytest fixtures and assertions |
| **Correctness** | Tests are executed automatically; only passing tests surface in reports |
| **Edge case handling** | Dedicated `edge_case_finder.py` agent identifies boundary and failure conditions |
| **Maintainability** | Generated tests follow pytest conventions with clear naming and docstrings |
| **CI integration** | GitHub Actions workflow included; API-first design supports any CI tool |

---

## 🛣️ Roadmap

- [ ] Advanced coverage heatmaps
- [ ] Multi-file dependency analysis
- [ ] Java & Go execution support
- [ ] Mutation testing
- [ ] Real-time streaming updates
- [ ] Authentication & team workspaces
- [ ] Persistent history dashboard

---

## 👥 Team — Osaka Vise

| Name | Role |
|---|---|
| **Aaron Rao** | AI Testing & Validation |
| **Aditi Karn** | System Architecture Lead |
| **Aryan Gupta** | UI/UX Developer |
| **Nitin Chugh** | Backend & API Engineer |
| **Vidushi Srivastava** | Presentation Lead |

---

## 📄 License

MIT © Team Osaka Vise — Built for the Capgemini Exceller AgentifAI Buildathon