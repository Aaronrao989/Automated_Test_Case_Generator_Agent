# Groq API Integration Setup Guide

## Overview

This project now uses the **Groq API** to generate AI-powered test cases using the `llama-3.1-8b-instant` language model. Groq provides fast, cost-effective inference for test case generation.

## Prerequisites

1. A Groq API account (free tier available)
2. Groq API key

## Step 1: Get Your Groq API Key

### Option A: Create a New Groq Account

1. Visit **https://console.groq.com**
2. Sign up for a free account (or sign in if you already have one)
3. Navigate to **API Keys** section
4. Click **"Create API Key"**
5. Copy your API key (you'll only see it once!)
6. Save it somewhere secure

### Option B: Use an Existing Groq Account

1. Go to **https://console.groq.com**
2. Sign in with your credentials
3. Navigate to **API Keys** section
4. Click **"Create API Key"** or copy an existing key

## Step 2: Configure Your API Key

### Update the `.env` File

Edit `backend/.env` and replace the placeholder with your actual API key:

```bash
# Before (placeholder):
GROQ_API_KEY=your-groq-api-key-here

# After (your actual key):
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Verify Configuration

Check that these values are set in `backend/.env`:

```bash
LLM_PROVIDER=groq
GROQ_API_KEY=<your-actual-key>
GROQ_MODEL=llama-3.1-8b-instant
```

## Step 3: Restart Services

After updating the `.env` file, restart the backend and Celery worker:

```bash
# Stop existing services (Ctrl+C in their terminals)
# Then restart:

# Terminal 1 - Backend API
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Celery Worker
cd backend
source venv/bin/activate
celery -A app.workers.celery_app worker --loglevel=info
```

## Step 4: Test the Integration

Run the integration test to verify Groq is working:

```bash
cd <project-root>
python test_groq_integration.py
```

Expected output:
```
======================================================================
GROQ API INTEGRATION TEST
======================================================================

[1] Checking Groq API key configuration...
✓ Groq API key is configured

[2] Creating analysis job...
  Created test repository: /tmp/test_repo_for_groq

[3] Starting analysis job...
✓ Job created: <job-id>

[4] Waiting for analysis to complete...
  Status: COMPLETED

[5] Checking generated tests...
✓ Generated 10 tests
  → 10 generated via Groq LLM

[6] Sample AI-Generated Test:
  Function: add
  Type: comprehensive
  Provider: groq

======================================================================
✓ GROQ INTEGRATION TEST PASSED
======================================================================
```

## How It Works

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js)                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                          │
│    POST /api/v1/analysis/start (new job)                   │
│    GET  /api/v1/analysis/{job_id} (get results)            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Celery Worker                              │
│  1. Scan repository structure                              │
│  2. Extract functions and source code                      │
│  3. Find edge cases                                        │
│  4. Generate tests using LLM ◄─────┐                       │
│  5. Execute tests (mock)            │                       │
│  6. Generate coverage report        │                       │
└─────────────────────────────────────┼───────────────────────┘
                                      │
                                      ▼
                            ┌──────────────────┐
                            │  Groq API        │
                            │  llama-3.1-8b    │
                            │  instant model   │
                            └──────────────────┘
```

### Test Generation Flow

1. **Repository Scan**: Extracts all functions from codebase
2. **Edge Case Detection**: Identifies potential test scenarios
3. **LLM Prompt Engineering**: Creates context-aware prompts
4. **Groq API Call**: Sends prompt to Groq's `llama-3.1-8b-instant` model
5. **Test Code Generation**: Receives AI-generated test code
6. **Result Storage**: Saves tests in database with metadata

### Example: Test Generation

**Input Function:**
```python
def divide(a, b):
    """Divide a by b"""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

**Generated Tests (via Groq):**
```python
import pytest
from module import divide

def test_divide_basic():
    """Test divide with basic input"""
    assert divide(10, 2) == 5.0

def test_divide_by_zero():
    """Test divide raises error for zero divisor"""
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(10, 0)

def test_divide_negative_numbers():
    """Test divide with negative numbers"""
    assert divide(-10, 2) == -5.0
    assert divide(10, -2) == -5.0

def test_divide_floats():
    """Test divide with float inputs"""
    assert divide(10.5, 2.0) == 5.25

def test_divide_edge_cases():
    """Test divide with edge cases"""
    assert divide(0, 5) == 0.0
    assert abs(divide(1, 3) - 0.333) < 0.01
```

## Monitoring API Usage

### In Groq Dashboard

1. Go to **https://console.groq.com**
2. Navigate to **Usage** section
3. View:
   - API calls made
   - Tokens used
   - Cost (if applicable)
   - Rate limit status

### In Your Application

Check the **Celery Worker Logs** to see LLM calls:

```
[LLM] Generating tests for add using Groq...
[LLM] ✓ Generated tests for add
[LLM] Generating tests for divide using Groq...
[LLM] ✓ Generated tests for divide
```

## Troubleshooting

### "Invalid API Key" Error

```
Error: Invalid API key provided
```

**Solution:**
- Verify your API key is copied correctly (no extra spaces)
- Check that the key starts with `gsk_`
- Make sure you've restarted the backend after updating `.env`

### "Rate Limit Exceeded"

```
Error: Rate limit exceeded
```

**Solution:**
- Free tier has rate limits (~30 requests/minute)
- Upgrade to paid plan for higher limits
- Add retry logic (already implemented)

### Tests Showing "demo" Instead of "groq"

```
"generated_by": "demo"
```

**Solution:**
- This means the API key wasn't found or wasn't valid
- Check that `GROQ_API_KEY` is set correctly in `backend/.env`
- Verify the key is not `your-groq-api-key-here` (placeholder)
- Restart the backend

### Connection Timeout

```
Error: Connection timeout
```

**Solution:**
- Groq servers may be temporarily down (rare)
- Check internet connection
- Check firewall/proxy settings
- Try again in a few moments

## API Costs

### Groq Free Tier

- Up to 30 requests per minute
- Limited to `llama-3.1-8b-instant` model
- Perfect for development and testing
- No credit card required

### Example Cost Calculation

For typical test generation:
- ~500 tokens per test
- 10 tests per analysis = 5,000 tokens
- Free tier includes generous limits

## Next Steps

1. ✅ Set up Groq API key
2. ✅ Update `backend/.env`
3. ✅ Restart services
4. ✅ Run `test_groq_integration.py` to verify
5. ✅ Submit code analysis jobs via the frontend
6. ✅ Monitor API usage in Groq dashboard
7. ✅ Scale up to paid plan if needed

## Important Notes

- **API Key Security**: Never commit `.env` with real API keys to version control
- **Rate Limiting**: Free tier limited to 30 req/min - suitable for development
- **Model**: `llama-3.1-8b-instant` is fast and cost-effective
- **Fallback**: If API key not configured, system generates demo tests automatically
- **Reproducibility**: AI-generated tests may vary slightly between runs

## Support

- **Groq Documentation**: https://groq.com/docs
- **Groq Console**: https://console.groq.com
- **API Reference**: https://console.groq.com/keys

---

## Quick Reference

| Item | Value |
|------|-------|
| API Provider | Groq |
| Model | llama-3.1-8b-instant |
| Rate Limit (Free) | 30 req/min |
| Cost | Free (with limits) or paid |
| Response Time | ~500ms average |
| Test Generation Per Job | 10-20 tests |

---

**Status**: ✅ Groq integration is now active in your system. Configure your API key to start generating real AI-powered tests!
