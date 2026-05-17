#!/usr/bin/env python3
"""
Test script to verify Groq API integration is working.
This will trigger an analysis and monitor Groq API calls.
"""

import requests
import time
import json
import subprocess
import os
from pathlib import Path

# Configuration
API_URL = "http://localhost:8000/api/v1"
BACKEND_DIR = Path(__file__).parent / "backend"

def test_groq_integration():
    """Test that Groq API is being called for test generation."""
    
    print("\n" + "="*70)
    print("GROQ API INTEGRATION TEST")
    print("="*70)
    
    # Step 1: Verify Groq API key is set
    print("\n[1] Checking Groq API key configuration...")
    env_file = BACKEND_DIR / ".env"
    if env_file.exists():
        with open(env_file) as f:
            content = f.read()
            if "GROQ_API_KEY=" in content:
                # Extract the key (not the value for security)
                for line in content.split('\n'):
                    if line.startswith('GROQ_API_KEY='):
                        key_part = line.split('=')[1]
                        if key_part and key_part != "your-groq-api-key-here":
                            print("✓ Groq API key is configured")
                        else:
                            print("✗ Groq API key is NOT set - using placeholder")
                        break
            else:
                print("✗ GROQ_API_KEY not found in .env")
    else:
        print("✗ .env file not found")
    
    # Step 2: Create an analysis job
    print("\n[2] Creating analysis job...")
    
    # Use user_story source type with sample code
    sample_code = """
def add(a, b):
    '''Add two numbers'''
    return a + b

def divide(a, b):
    '''Divide a by b'''
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def greet(name):
    '''Greet someone'''
    if not name:
        raise ValueError("Name cannot be empty")
    return f"Hello, {name}!"
"""
    
    # Step 3: Start analysis
    print("\n[3] Starting analysis job...")
    response = requests.post(
        f"{API_URL}/analysis/start",
        json={
            "source_type": "user_story",
            "source_data": sample_code
        }
    )
    
    if response.status_code == 200:
        job_data = response.json()
        job_id = job_data.get("job_id")
        print(f"✓ Job created: {job_id}")
    else:
        print(f"✗ Failed to create job: {response.status_code}")
        print(f"  Response: {response.text}")
        return False
    
    # Step 4: Wait for job to complete
    print("\n[4] Waiting for analysis to complete...")
    max_wait = 120  # 120 seconds
    start_time = time.time()
    status = "PENDING"
    data = None
    
    while status in ["PENDING", "IN_PROGRESS"] and time.time() - start_time < max_wait:
        response = requests.get(f"{API_URL}/analysis/{job_id}")
        
        # 202 means job is still processing
        if response.status_code == 202:
            print(f"  Status: PROCESSING                  ", end='\r')
            time.sleep(2)
        elif response.status_code == 200:
            data = response.json()
            status = data.get("status", "UNKNOWN")
            print(f"  Status: {status}          ", end='\r')
            if status in ["PENDING", "IN_PROGRESS"]:
                time.sleep(2)
        else:
            print(f"✗ Failed to get job status: {response.status_code}")
            return False
    
    print(f"  Status: COMPLETED             ")
    
    # Step 5: Check results
    print("\n[5] Checking generated tests...")
    
    # Get final results
    response = requests.get(f"{API_URL}/analysis/{job_id}")
    
    if response.status_code in [200, 202]:
        if response.status_code == 200:
            analysis_result = response.json()
        else:
            # 202 means still processing - should not happen at this point
            print("✗ Job is still processing (timeout)")
            return False
        
        # Check for tests
        tests = analysis_result.get("tests", [])
        print(f"✓ Generated {len(tests)} tests")
        
        if tests:
            # Check if tests are AI-generated (have "generated_by": "groq")
            ai_tests = [t for t in tests if t.get("generated_by") == "groq"]
            print(f"  → {len(ai_tests)} generated via Groq LLM")
            
            if ai_tests:
                print("\n[6] Sample AI-Generated Test:")
                sample_test = ai_tests[0]
                print(f"  Function: {sample_test.get('target_function')}")
                print(f"  Type: {sample_test.get('test_type')}")
                print(f"  Provider: {sample_test.get('generated_by')}")
                print(f"\n  Test Code Preview:")
                test_content = sample_test.get('content', '')[:300]
                for line in test_content.split('\n')[:5]:
                    print(f"    {line}")
                if len(test_content) > 300:
                    print("    ...")
            
            print("\n✓ SUCCESS: Groq API integration is working!")
            print("  - Tests are being generated via LLM")
            print("  - AI-generated tests are in the results")
            return True
        else:
            print("✗ No tests were generated")
            print(f"  Full result: {json.dumps(analysis_result, indent=2)}")
            return False
    else:
        print(f"✗ Failed to get results: {response.status_code}")
        return False

if __name__ == "__main__":
    try:
        success = test_groq_integration()
        
        print("\n" + "="*70)
        if success:
            print("✓ GROQ INTEGRATION TEST PASSED")
        else:
            print("✗ GROQ INTEGRATION TEST FAILED")
        print("="*70 + "\n")
        
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
