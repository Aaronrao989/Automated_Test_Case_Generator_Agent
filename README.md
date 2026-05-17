# Automated Test Case Generator Agent

An AI-powered application that automatically generates comprehensive test cases from source code, identifies edge cases, and provides code coverage analysis.

## 🚀 Features

- **Repository Analysis**: Automatically scan and analyze code structure, functions, and dependencies
- **Multi-Agent Architecture**: Leverages 7 specialized agents for different aspects of test generation
- **Test Generation**: Creates unit tests, integration tests, edge case tests, and boundary tests
- **Edge Case Detection**: Automatically identifies potential edge cases, null/empty inputs, boundary conditions, concurrency issues, and API failures
- **Coverage Analysis**: Computes code coverage and suggests missing test scenarios
- **CI/CD Integration**: Generates GitHub PR comments with analysis results
- **Multi-Language Support**: Supports Python, JavaScript, TypeScript, Java, Go, C++, and Rust
- **Sandbox Execution**: Runs tests in isolated Docker containers for safety

## 📋 Project Structure

```
Automated_Test_Case_Generator_Agent/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── agents/            # Multi-agent system
│   │   │   ├── repo_scanner.py         # Scan repository structure
│   │   │   ├── code_understanding.py   # Analyze code semantics
│   │   │   ├── edge_case_finder.py     # Identify edge cases
│   │   │   ├── test_writer.py          # Generate test code
│   │   │   ├── test_executor.py        # Execute tests in sandbox
│   │   │   ├── coverage.py             # Analyze coverage
│   │   │   ├── ci_agent.py             # CI/CD integration
│   │   │   └── orchestrator.py         # Coordinate agents
│   │   ├── api/                # FastAPI routes
│   │   ├── models/             # Database models
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── core/               # Configuration
│   │   ├── db/                 # Database setup
│   │   ├── workers/            # Celery tasks
│   │   └── main.py             # FastAPI app
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                   # Next.js 15 frontend
│   ├── src/app/
│   │   ├── page.tsx            # Landing page
│   │   ├── upload/             # Repository upload page
│   │   ├── dashboard/          # Analysis dashboard
│   │   ├── tests/              # Tests viewer
│   │   └── layout.tsx          # Main layout
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml          # Container orchestration
├── docs/api/openapi.yml        # API specification
└── .github/workflows/ci.yml    # CI/CD pipeline
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Celery** - Async task queue
- **Redis** - Message broker and cache
- **PostgreSQL** - Primary database
- **Docker** - Sandboxed test execution
- **LangChain/LangGraph** - AI agent orchestration
- **OpenAI** - LLM for code analysis (optional)

### Frontend
- **Next.js 15** - React framework with TypeScript
- **TailwindCSS** - Utility-first CSS
- **shadcn/ui** - Component library
- **Zustand** - State management
- **Recharts** - Data visualization
- **Monaco Editor** - Code editor (optional)

### Observability
- **OpenTelemetry** - Tracing (optional)
- **LangSmith** - LLM traces (optional)
- **Structured logging** - Application logging

## 📦 Installation & Setup

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for frontend)
- Python 3.11+ (for backend)
- Git

### Quick Start with Docker

1. **Clone and navigate to project:**
   ```bash
   cd Automated_Test_Case_Generator_Agent
   ```

2. **Set environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start all services:**
   ```bash
   docker-compose up --build
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Manual Setup (Development)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Services (in separate terminals):**
```bash
# Redis
docker run -d -p 6379:6379 redis:7

# PostgreSQL
docker run -d -p 5432:5432 \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=appdb \
  postgres:15

# Celery Worker
cd backend
celery -A app.workers.celery_app worker --loglevel=info
```

## 🤖 Multi-Agent Architecture

### 1. **Repo Scanner Agent**
   - Scans repository structure
   - Classifies programming languages
   - Extracts file tree and functions

### 2. **Code Understanding Agent**
   - Analyzes function signatures
   - Extracts function intent
   - Computes code complexity

### 3. **Edge Case Finder Agent**
   - Identifies null/None cases
   - Detects empty input scenarios
   - Finds boundary conditions
   - Detects concurrency issues
   - Identifies API failure points

### 4. **Test Writer Agent**
   - Generates unit tests
   - Creates integration tests
   - Produces edge case tests
   - Generates boundary tests

### 5. **Test Executor Agent**
   - Runs tests in Docker sandbox
   - Captures stdout/stderr
   - Reports pass/fail status

### 6. **Coverage Agent**
   - Computes code coverage metrics
   - Ranks uncovered code by importance
   - Suggests missing test scenarios

### 7. **CI Agent**
   - Creates GitHub PR comments
   - Publishes coverage reports
   - Generates check runs

## 📡 API Endpoints

### Analysis Management
- `POST /api/v1/analysis/start` - Start analysis from GitHub URL/text
- `POST /api/v1/analysis/upload` - Upload ZIP file for analysis
- `GET /api/v1/analysis/{job_id}` - Get analysis results

### Health
- `GET /health` - Health check endpoint

### Response Format
```json
{
  "job_id": "uuid",
  "status": "COMPLETED|IN_PROGRESS|FAILED",
  "structure": {
    "languages": {"python": 45, "javascript": 30},
    "total_files": 75,
    "functions": [...]
  },
  "edge_cases": [...],
  "tests": [...],
  "coverage": {
    "total_coverage": 85.5,
    "file_coverage": {...}
  }
}
```

## 🧪 Usage Examples

### 1. Analyze a GitHub Repository
```bash
curl -X POST http://localhost:8000/api/v1/analysis/start \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "github_url",
    "source_data": "https://github.com/python/cpython"
  }'
```

### 2. Upload a ZIP File
```bash
curl -X POST http://localhost:8000/api/v1/analysis/upload \
  -F "file=@repo.zip"
```

### 3. Check Analysis Status
```bash
curl http://localhost:8000/api/v1/analysis/abc123
```

## 🎯 Supported Languages

| Language   | Status | Test Runners |
|-----------|--------|-------------|
| Python    | ✅     | pytest      |
| JavaScript| ✅     | jest        |
| TypeScript| ✅     | jest        |
| Java      | 🔄     | junit       |
| Go        | 🔄     | testing     |
| C++       | 🔄     | gtest       |
| Rust      | 🔄     | cargo test  |

## 🔒 Security Features

- **Sandboxed Execution**: All tests run in isolated Docker containers
- **No Host Execution**: Generated tests cannot access host system
- **Secret Vault**: Environment variables managed securely
- **Rate Limiting**: API endpoints protected from abuse
- **Input Validation**: All inputs validated with Pydantic

## 📊 Dashboard Features

- **Repository Overview**: Language breakdown, file statistics
- **Coverage Heatmap**: Visual representation of code coverage
- **Test Results**: Pass/fail statistics and execution times
- **Edge Case Summary**: List of identified edge cases
- **Execution Logs**: Detailed test execution output

## 🚀 Deployment

### Docker Compose Production
```bash
docker-compose -f docker-compose.yml up -d
```

### GitHub Actions CI/CD
The `.github/workflows/ci.yml` file includes:
- Automated builds on push
- Test execution
- Coverage reporting
- PR comment generation

### Environment Variables
```bash
# Backend
DATABASE_URL=postgresql://user:pass@db:5432/appdb
REDIS_URL=redis://redis:6379/0
OPENAI_API_KEY=sk-...
LANGSMITH_API_KEY=...

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📈 Roadmap

- [ ] Advanced LLM integration for test generation
- [ ] Real-time collaboration features
- [ ] Custom test templates
- [ ] Team workspaces
- [ ] Test flakiness detection
- [ ] Mutation testing support
- [ ] Performance regression testing
- [ ] Mobile app (React Native)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 💬 Support

- **Documentation**: `/docs/api/openapi.yml`
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

## 🎉 Credits

Built with cutting-edge AI agents and modern web technologies to revolutionize test automation.

---

**Happy Testing! 🚀**

