# System Architecture

Detailed technical architecture of the Automated Test Case Generator Agent.

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     User Interface Layer                        │
│                 (Next.js 15 - React Frontend)                   │
│  Landing → Upload → Analysis → Dashboard → Tests → Coverage    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    REST API (JSON)
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                  API Layer (FastAPI)                            │
│  /api/v1/analysis/start                                         │
│  /api/v1/analysis/upload                                        │
│  /api/v1/analysis/{job_id}                                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
        ┌───────────▼──────┐  ┌──────▼──────────┐
        │ Async Task Queue │  │ Database Layer  │
        │  (Celery/Redis)  │  │  (PostgreSQL)   │
        └────────┬─────────┘  └────────┬────────┘
                 │                     │
        ┌────────▼────────┐    ┌──────▼──────────┐
        │ Worker Processes│    │  Data Models    │
        │  (Test Engine)  │    │  Schemas        │
        └────────┬────────┘    └─────────────────┘
                 │
        ┌────────▼──────────────────┐
        │  Multi-Agent System       │
        │  (Test Generation Engine) │
        └────────┬──────────────────┘
                 │
        ┌────────┴────────────────────────────────┐
        │                                         │
    ┌───▼────┐ ┌───────────┐ ┌──────────┐ ┌─────▼────┐
    │ Repo   │ │ Code      │ │ Edge     │ │ Test     │
    │Scanner │→│Understanding│→│CaseFinder│→│Writer   │
    └────────┘ └───────────┘ └──────────┘ └──────────┘
        │          │             │             │
        └──────────┴─────────────┴─────────────┘
                 │
    ┌────────────▼─────────────┐
    │ Test Executor Agent      │
    │ (Docker Sandbox)         │
    └────────────┬─────────────┘
                 │
        ┌────────▼──────────┐
        │ Coverage Agent    │
        │ CI Agent          │
        └──────────────────┘
```

## Component Details

### 1. Frontend Layer (Next.js)

**Pages:**
- `page.tsx` - Landing page with feature showcase
- `upload/page.tsx` - Repository input interface
- `dashboard/page.tsx` - Results visualization
- `tests/page.tsx` - Generated tests viewer

**State Management:**
- Zustand store (`lib/store.ts`) for app-wide state
- Local React state for form handling
- API integration with async/await

**Visualization:**
- Recharts for coverage charts (BarChart, PieChart, LineChart)
- Tailwind CSS for responsive design
- shadcn/ui for consistent components

### 2. API Layer (FastAPI)

**Endpoints:**

```python
POST /api/v1/analysis/start
├─ Payload: source_type, source_data
├─ Response: job_id, status, created_at
└─ Creates async task

POST /api/v1/analysis/upload
├─ Payload: ZIP file
├─ Response: job_id, status
└─ Saves file, creates async task

GET /api/v1/analysis/{job_id}
├─ Response: Full analysis results
├─ Status codes:
│  ├─ 200: Completed
│  ├─ 202: In progress
│  ├─ 404: Not found
│  └─ 500: Failed
└─ Returns: structure, tests, coverage, edge_cases

GET /health
├─ Response: status check
└─ Used for load balancer health checks
```

### 3. Data Layer

**Database Schema:**

```sql
AnalysisJob
├─ id (UUID, PK)
├─ status (ENUM: PENDING, IN_PROGRESS, COMPLETED, FAILED)
├─ source_type (string)
├─ source_data (text)
├─ created_at (timestamp)
├─ updated_at (timestamp)
└─ error_message (optional)

RepoStructure
├─ id (UUID, PK)
├─ job_id (FK)
├─ languages (JSON)
├─ files (JSON - tree structure)
├─ functions (JSON - array of functions)
└─ dependencies (JSON - dependency graph)

GeneratedTest
├─ id (UUID, PK)
├─ job_id (FK)
├─ test_type (ENUM: unit, integration, negative, boundary)
├─ file_path (string)
├─ content (text - test code)
├─ language (string)
├─ target_function (string)
└─ created_at (timestamp)

TestExecutionResult
├─ id (UUID, PK)
├─ job_id (FK)
├─ test_id (FK)
├─ status (ENUM: PASSED, FAILED, ERROR)
├─ duration (float)
├─ output (text)
├─ error (optional)
└─ created_at (timestamp)

CoverageReport
├─ id (UUID, PK)
├─ job_id (FK)
├─ total_coverage (float - percentage)
├─ covered_lines (int)
├─ total_lines (int)
├─ file_coverage (JSON)
├─ uncovered_code (JSON)
└─ created_at (timestamp)

EdgeCase
├─ id (UUID, PK)
├─ job_id (FK)
├─ function_name (string)
├─ edge_case_type (string)
├─ description (text)
├─ suggested_test (text)
└─ created_at (timestamp)
```

### 4. Task Queue (Celery + Redis)

**Flow:**

```
User Request
    │
    ├─→ Create AnalysisJob (PENDING)
    │
    ├─→ Queue Task in Redis
    │
    └─→ Return job_id (202 Accepted)
         │
         └─→ Client polls /api/v1/analysis/{job_id}
              │
              └─→ Returns 202 while processing
                  │
                  └─→ Returns 200 with results when done
```

**Celery Task:**

```python
@celery_app.task
def analyze_repository_task(job_id, source_type, source_data):
    # 1. Update job status to IN_PROGRESS
    # 2. Run orchestrator.analyze_repository()
    # 3. Store results in database
    # 4. Update job status to COMPLETED
    # 5. Handle errors and set FAILED status
```

### 5. Multi-Agent System

**Agent Orchestration Flow:**

```
analyze_repository()
    │
    ├─→ Repo Scanner Agent
    │   ├─ Scan directory structure
    │   ├─ Detect languages
    │   ├─ Extract functions/classes
    │   └─ Build dependency graph
    │
    ├─→ Code Understanding Agent
    │   ├─ Analyze each function
    │   ├─ Extract signatures
    │   ├─ Infer intent
    │   └─ Compute complexity
    │
    ├─→ Edge Case Finder Agent
    │   ├─ Find null/None cases
    │   ├─ Find empty inputs
    │   ├─ Find boundaries
    │   ├─ Find concurrency issues
    │   └─ Find API failures
    │
    ├─→ Test Writer Agent
    │   ├─ Generate unit tests
    │   ├─ Generate edge case tests
    │   ├─ Generate boundary tests
    │   ├─ Generate integration tests
    │   └─ Generate negative tests
    │
    ├─→ Test Executor Agent
    │   ├─ Run tests in Docker
    │   ├─ Capture output
    │   ├─ Record results
    │   └─ Handle errors
    │
    ├─→ Coverage Agent
    │   ├─ Compute coverage metrics
    │   ├─ Identify uncovered code
    │   ├─ Rank by importance
    │   └─ Suggest improvements
    │
    └─→ CI Agent
        ├─ Create PR comments
        ├─ Export reports
        └─ Publish coverage
```

### 6. Docker Sandbox Execution

**Security Model:**

```
Host System
    │
    └─→ Docker Daemon
         │
         └─→ Container (test-executor-xxx)
              ├─ Limited resources
              ├─ Read-only repo
              ├─ Isolated network
              ├─ No host access
              └─ Timeout enforcement
```

**Test Execution Process:**

```python
def execute_tests(tests, language):
    # 1. Create temp file with test code
    # 2. Create Docker container with:
    #    - Single test file (mounted read-only)
    #    - Test runner (pytest/jest/etc)
    #    - Timeout (30 seconds)
    #    - Memory limit (512MB)
    #    - CPU limit (1 core)
    # 3. Execute test command
    # 4. Capture stdout/stderr
    # 5. Parse results
    # 6. Clean up container
    # 7. Return results
```

## Data Flow Examples

### Example 1: GitHub Repository Analysis

```
User Input
  ↓
POST /api/v1/analysis/start
{
  "source_type": "github_url",
  "source_data": "https://github.com/repo"
}
  ↓
Create AnalysisJob (PENDING)
  ↓
Queue Celery Task
  ↓
Return {job_id: "abc123", status: "PENDING"}
  ↓
Client polls GET /api/v1/analysis/abc123
  ↓
(Background) Celery Worker:
  - Clone GitHub repo
  - Run Repo Scanner Agent
  - Run Code Understanding Agent
  - Run Edge Case Finder Agent
  - Run Test Writer Agent
  - Run Test Executor Agent
  - Run Coverage Agent
  - Store all results in DB
  - Update job status to COMPLETED
  ↓
GET /api/v1/analysis/abc123 returns full results
  ↓
Frontend displays dashboard with results
```

### Example 2: Test Execution Flow

```
Test Writer generates test file:
  ↓
def test_function_null_input():
    with pytest.raises(TypeError):
        function(None)
  ↓
Test Executor Agent receives test
  ↓
1. Create temp file: /tmp/test_abc123.py
2. Start Docker container:
   docker run --rm \
     --memory="512m" \
     --cpus="1" \
     --volume /tmp/test_abc123.py:/test.py:ro \
     python:3.11-slim \
     python -m pytest /test.py -v
  ↓
3. Capture output:
   "PASSED test_function_null_input"
  ↓
4. Parse and store result:
   {
     "id": "result_xyz",
     "status": "PASSED",
     "output": "PASSED test_function_null_input",
     "duration": 0.234
   }
  ↓
5. Clean up container
  ↓
Return result to database
```

## Scalability Architecture

### Horizontal Scaling

```
Load Balancer
    │
    ├─→ Backend Instance 1
    ├─→ Backend Instance 2
    ├─→ Backend Instance 3
    │
    └─→ Shared Services:
        ├─ PostgreSQL (primary + replicas)
        ├─ Redis (cluster)
        ├─ Celery Workers (auto-scaled)
        └─ File Storage (S3 or similar)
```

### Caching Strategy

```
Request
  │
  ├─→ Check Redis cache
  │   ├─ HIT: Return cached result
  │   └─ MISS: Proceed to next step
  │
  ├─→ Check database
  │   ├─ HIT: Cache and return
  │   └─ MISS: Generate and cache
  │
  └─→ Return result
```

## Error Handling

```
Errors are categorized:

1. Validation Errors (400)
   - Invalid input format
   - Missing required fields
   - Invalid URL/file

2. Not Found (404)
   - Job doesn't exist
   - Results deleted

3. Processing Errors (500)
   - Database connection failed
   - Test execution failed
   - Parsing error

4. Service Errors (503)
   - Redis unavailable
   - Database unavailable
   - Worker queue full

Each error:
- Logged with context
- Stored in AnalysisJob.error_message
- Returned to client with details
- Monitored for alerting
```

## Security Model

### Input Validation

```
Every API input:
1. Schema validation (Pydantic)
2. Size limits (MAX_FILE_SIZE)
3. Type checking
4. SQL injection prevention (SQLAlchemy ORM)
5. XSS prevention (React escaping)
```

### Execution Sandbox

```
Generated tests run:
- In isolated Docker container
- With resource limits
- Without network access
- No access to host files
- Automatic timeout (30s)
- Container cleanup on exit
```

### Data Protection

```
Sensitive data:
- API keys: Environment variables (not in code)
- Database passwords: Secrets manager
- User data: Encrypted at rest (optional)
- Test code: Temporary files (auto-deleted)
```

## Monitoring & Observability

```
Metrics collected:
- Request latency
- Error rates
- Task queue depth
- Database connection pool
- Cache hit rates
- Worker utilization
- Test execution times
- Coverage trends

Logging:
- Structured JSON logs
- Correlation IDs
- Trace context
- Error stack traces

Alerts:
- Error rate > 5%
- Response time > 5s
- Queue depth > 100
- Worker unavailable
- Database connection failures
```

## Performance Optimization

### Database

```
- Connection pooling (pool_size=20)
- Query optimization with indexes
- Prepared statements
- Result caching
```

### Cache

```
- Redis for:
  - Job results (TTL: 7 days)
  - API responses (TTL: 1 hour)
  - Function analysis (TTL: 30 days)
```

### Async Processing

```
- Long operations in Celery
- Non-blocking I/O
- Batch processing where possible
```

## Disaster Recovery

```
Backup Strategy:
- Daily automated DB backups (7-day retention)
- Point-in-time recovery (14 days)
- Test backups monthly

RTO: 1 hour (Recovery Time Objective)
RPO: 1 hour (Recovery Point Objective)

Failover:
- Database: Read replicas for automatic failover
- Redis: Redis Sentinel or Cluster
- API: Load balancer with health checks
```

---

For deployment details, see DEPLOYMENT.md
For development setup, see DEVELOPMENT.md
For API documentation, see docs/api/openapi.yml
