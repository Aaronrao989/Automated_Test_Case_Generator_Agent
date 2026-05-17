# Automated Test Case Generator Agent

AI-powered automated test generation platform using:

- FastAPI
- Celery
- Redis
- PostgreSQL
- Groq LLM
- Pytest
- Coverage.py

---

# Features

- Repository scanning
- Python & JavaScript support
- AI-generated test cases
- Edge case analysis
- Automated pytest execution
- Coverage analysis
- Background task processing
- ZIP repository uploads
- GitHub repository analysis

---

# Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI |
| Queue | Celery |
| Broker | Redis |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| AI | Groq |
| Testing | Pytest |
| Coverage | coverage.py |

---

# Project Structure

```text
backend/
│
├── app/
│   ├── agents/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── schemas/
│   └── workers/
│
├── tests/
│
├── generated_tests/
│
├── requirements.txt
├── pytest.ini
├── run.py
└── README.md
```

---

# Setup

## 1. Clone Repository

```bash
git clone <repo-url>
cd backend
```

---

## 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate:

### Mac/Linux

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create `.env`

```env
DATABASE_URL=postgresql://username:password@localhost:5432/automated_test_generator

REDIS_URL=redis://localhost:6379/0

CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

LLM_PROVIDER=groq

GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.1-8b-instant

UPLOAD_DIR=/tmp/uploads
MAX_FILE_SIZE=104857600
```

---

# Run Services

## PostgreSQL

Start PostgreSQL locally.

---

## Redis

```bash
redis-server
```

---

# Run API Server

```bash
python run.py
```

Server:

```text
http://localhost:8000
```

Swagger Docs:

```text
http://localhost:8000/docs
```

---

# Run Celery Worker

```bash
celery -A app.workers.celery_app.celery_app worker --loglevel=info
```

---

# Run Tests

```bash
pytest
```

---

# API Endpoints

## Health

```http
GET /health
```

---

## Start Analysis

```http
POST /api/v1/analysis/start
```

Example:

```json
{
  "source_type": "code_snippet",
  "source_data": "def add(a,b): return a+b"
}
```

---

## Upload ZIP Repository

```http
POST /api/v1/analysis/upload
```

---

## Get Analysis Result

```http
GET /api/v1/analysis/{job_id}
```

---

## Delete Job

```http
DELETE /api/v1/analysis/{job_id}
```

---

# Supported Source Types

- github_url
- zip_file
- code_snippet
- user_story

---

# Supported Languages

- Python
- JavaScript
- TypeScript

---

# Coverage

Coverage reports are generated using:

```bash
coverage.py
```

---

# Notes

- Generated tests are stored in:
  `generated_tests/`
- Celery + Redis required for async jobs
- Groq API key required for AI test generation

---

# License

MIT License