# Quick Start Guide

Get the Automated Test Case Generator Agent up and running in 5 minutes!

## Prerequisites

- Docker & Docker Compose installed
- (Optional) Node.js 18+ and Python 3.11+ for local development

## Option 1: Docker Compose (Recommended)

### 1. Clone and Enter Project

```bash
cd Automated_Test_Case_Generator_Agent
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env if needed (defaults should work locally)
```

### 3. Start Services

```bash
docker-compose up --build
```

This will start:
- Frontend (http://localhost:3000)
- Backend API (http://localhost:8000)
- PostgreSQL database
- Redis cache
- Celery worker

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **API**: http://localhost:8000/api/v1/...

### 5. Stop Services

```bash
docker-compose down
```

## Option 2: Local Development

### Backend

```bash
# 1. Create virtual environment
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start services in Docker
cd ..
docker-compose up -d db redis

# 4. Run backend server
cd backend
uvicorn app.main:app --reload
```

Backend runs at: http://localhost:8000

### Frontend (new terminal)

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: http://localhost:3000

### Celery Worker (another terminal)

```bash
cd backend
celery -A app.workers.celery_app worker --loglevel=info
```

## First Steps

### 1. Upload a Repository

1. Open http://localhost:3000
2. Click "Get Started"
3. Choose upload method:
   - GitHub URL: Paste a GitHub repository URL
   - ZIP File: Upload a code repository
   - Paste Code: Directly paste code

Example GitHub URLs:
- https://github.com/python/cpython (large)
- https://github.com/torvalds/linux (very large)
- https://github.com/kubernetes/kubernetes (very large)

For testing, try creating a simple test repository with Python/JavaScript code.

### 2. View Analysis Results

1. After uploading, you'll be redirected to the dashboard
2. The page will show:
   - Repository structure and languages used
   - Identified edge cases
   - Generated tests
   - Code coverage report

### 3. View Generated Tests

1. Click on "Tests" in the navigation
2. See generated test code
3. Choose between unit, edge case, and integration tests
4. View test statistics

## API Usage

### Start Analysis

```bash
curl -X POST http://localhost:8000/api/v1/analysis/start \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "github_url",
    "source_data": "https://github.com/repo/name"
  }'

# Response:
# {
#   "job_id": "abc123",
#   "status": "PENDING",
#   "created_at": "2024-01-15T10:30:00"
# }
```

### Check Status

```bash
curl http://localhost:8000/api/v1/analysis/abc123

# Response includes:
# - status: PENDING, IN_PROGRESS, or COMPLETED
# - structure: Languages, files, functions
# - edge_cases: Identified edge cases
# - tests: Generated tests
# - coverage: Coverage report
```

### Upload ZIP File

```bash
curl -X POST http://localhost:8000/api/v1/analysis/upload \
  -F "file=@path/to/repo.zip"

# Response:
# {
#   "job_id": "xyz789",
#   "status": "PENDING"
# }
```

## Troubleshooting

### Port Already in Use

Change port in the command:
```bash
uvicorn app.main:app --port 8001
npm run dev -- -p 3001
```

### Database Connection Error

Check PostgreSQL is running:
```bash
docker ps | grep postgres
```

Or restart services:
```bash
docker-compose restart db
```

### Redis Connection Error

Check Redis is running:
```bash
docker ps | grep redis
```

### Celery Worker Issues

Verify Redis connection:
```bash
redis-cli ping
# Should return: PONG
```

Restart worker:
```bash
pkill -f celery
celery -A app.workers.celery_app worker --loglevel=info
```

### Module Import Errors

Reinstall dependencies:
```bash
# Backend
pip install -r requirements.txt --force-reinstall

# Frontend
npm install --force
```

## Next Steps

1. **Explore the Dashboard**: Analyze your own code
2. **Check Generated Tests**: Review the test code in the UI
3. **View Coverage Report**: See which parts of code are covered
4. **Read Documentation**: 
   - README.md - Full feature list
   - ARCHITECTURE.md - System design
   - DEVELOPMENT.md - Development setup
   - DEPLOYMENT.md - Production deployment

## Features to Try

✅ **Repository Analysis**
- Supports GitHub URLs, ZIP files, or direct code paste
- Detects multiple programming languages
- Extracts functions and classes
- Maps dependencies

✅ **Test Generation**
- Generates unit tests
- Creates integration tests
- Identifies edge cases
- Generates boundary tests
- Creates negative tests

✅ **Coverage Analysis**
- Computes code coverage percentage
- Shows file-by-file coverage
- Identifies uncovered code
- Suggests test improvements

✅ **CI/CD Integration**
- Generates GitHub PR comments
- Exports test reports
- Publishes coverage metrics

## Performance Tips

1. **For Large Repositories**: 
   - May take 2-5 minutes for analysis
   - Limit analysis to specific directories if needed

2. **For Local Development**:
   - Use smaller test repositories
   - Keep database queries simple

3. **For Production**:
   - Scale Celery workers based on load
   - Enable caching layer
   - Use database replicas

## Getting Help

1. Check the documentation:
   - README.md
   - DEVELOPMENT.md
   - ARCHITECTURE.md

2. Review API documentation:
   - Visit http://localhost:8000/docs (Swagger UI)
   - See docs/api/openapi.yml

3. Check logs:
   ```bash
   docker-compose logs backend
   docker-compose logs frontend
   docker-compose logs worker
   ```

## Example Workflow

```
1. Start services
   docker-compose up --build

2. Open http://localhost:3000

3. Upload GitHub repo
   https://github.com/pallets/flask (Good for testing)

4. Wait for analysis (1-2 minutes)

5. View results on dashboard
   - Repository structure
   - Edge cases found
   - Tests generated

6. Check generated tests
   Navigate to /tests page

7. View coverage report
   Back on dashboard

8. Integrate with your CI/CD
   Add GitHub token to .env
   Tests will auto-comment on PRs
```

## Common Commands

```bash
# Start everything
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Rebuild images
docker-compose build --no-cache

# Run database migrations
docker-compose exec backend alembic upgrade head

# Drop and recreate database
docker-compose down -v
docker-compose up

# Run tests
cd backend && pytest tests/ -v

# Format code
cd backend && black app tests
cd frontend && npm run lint --fix
```

## What's Next?

- 📖 Read the full [README.md](README.md)
- 🏗️ Understand the [Architecture](ARCHITECTURE.md)
- 🚀 Deploy to [Production](DEPLOYMENT.md)
- 💻 Set up [Local Development](DEVELOPMENT.md)

---

**Enjoy! 🎉**

For questions or issues, check the documentation or open an issue on GitHub.
