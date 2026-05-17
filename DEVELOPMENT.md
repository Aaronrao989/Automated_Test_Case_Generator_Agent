# Development Guide

This guide walks you through setting up the Automated Test Case Generator Agent for local development.

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15
- Redis 7
- Git

## Project Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Automated_Test_Case_Generator_Agent
```

### 2. Environment Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your local settings (especially if using custom ports or LLM keys).

## Backend Setup

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start Supporting Services

Option A: Using Docker

```bash
docker run -d -p 5432:5432 \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=appdb \
  postgres:15

docker run -d -p 6379:6379 redis:7
```

Option B: Using Docker Compose (from root directory)

```bash
cd ..
docker-compose up -d db redis
```

### 4. Initialize Database

```bash
# Create tables
python -c "from app.db.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

### 5. Start the Backend Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: http://localhost:8000
API Documentation: http://localhost:8000/docs

### 6. Start Celery Worker (in another terminal)

```bash
cd backend
celery -A app.workers.celery_app worker --loglevel=info
```

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Development Server

```bash
npm run dev
```

The frontend will be available at: http://localhost:3000

### 3. Build for Production

```bash
npm run build
npm start
```

## Running Tests

### Backend Tests

```bash
cd backend
pytest tests/ -v
pytest tests/ -v --cov=app  # With coverage
```

### Frontend Tests

```bash
cd frontend
npm run test
npm run lint
```

## Docker Development

### Build All Services

```bash
docker-compose build
```

### Start All Services

```bash
docker-compose up
```

### View Logs

```bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f worker
```

### Stop Services

```bash
docker-compose down
```

## Database Migrations

### Create New Migration

```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

### Apply Migrations

```bash
alembic upgrade head
```

### Rollback

```bash
alembic downgrade -1
```

## API Development

### Add New Endpoints

1. Create route in `app/api/routes.py`
2. Define request/response models in `app/schemas/`
3. Update `docs/api/openapi.yml`

### Test Endpoints

Use the interactive API docs at: http://localhost:8000/docs

Or use curl:

```bash
curl -X GET http://localhost:8000/health
curl -X POST http://localhost:8000/api/v1/analysis/start \
  -H "Content-Type: application/json" \
  -d '{"source_type":"github_url","source_data":"https://github.com/repo"}'
```

## Debugging

### Backend Debugging

Use VS Code with Python debugger:

```bash
# In VS Code, select the interpreter from the venv
# Set breakpoints and run with Python debugger
```

Or use pdb:

```python
import pdb; pdb.set_trace()
```

### Frontend Debugging

Use browser DevTools or VS Code with the Debugger extension.

### Check Celery Tasks

```bash
# Monitor Celery events
celery -A app.workers.celery_app events
```

## Common Issues

### Database Connection Error

- Ensure PostgreSQL is running: `docker ps | grep postgres`
- Check DATABASE_URL in `.env`
- Verify credentials match docker-compose.yml

### Redis Connection Error

- Ensure Redis is running: `docker ps | grep redis`
- Check REDIS_URL in `.env`

### Port Already in Use

- Change port in command: `uvicorn app.main:app --port 8001`
- Or kill the process: `lsof -i :8000` and `kill -9 <PID>`

### Module Import Errors

- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

## Development Workflow

1. Create a feature branch:
   ```bash
   git checkout -b feature/my-feature
   ```

2. Make changes and test:
   ```bash
   pytest tests/ -v
   npm run lint
   ```

3. Commit with clear messages:
   ```bash
   git commit -m "feat: add new feature"
   ```

4. Push and create a Pull Request:
   ```bash
   git push origin feature/my-feature
   ```

## Code Style

- **Python**: Follow PEP 8 using `black`
- **Frontend**: Follow ESLint config

Run formatters:

```bash
# Backend
black app tests

# Frontend
npm run lint --fix
```

## Performance Profiling

### Backend Profiling

```python
from app.agents.repo_scanner import RepoScannerAgent
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # Top 10 functions
```

## Documentation

- API OpenAPI Spec: `docs/api/openapi.yml`
- README: `README.md`
- This guide: `DEVELOPMENT.md`

## Getting Help

- Check existing issues and PRs
- Review the code comments and docstrings
- Ask in project discussions

Happy coding! 🚀
