"""
Tests for LLMTestGenerator.
"""

from app.agents.llm_test_generator import (
    LLMTestGenerator
)


# ==========================================================
# INITIALIZATION
# ==========================================================

def test_llm_generator_initialization():

    generator = LLMTestGenerator()

    assert generator is not None

    assert generator.model is not None


# ==========================================================
# CLEAN CODE RESPONSE
# ==========================================================

def test_clean_code_response():

    generator = LLMTestGenerator()

    raw = """
```python
def test_sample():
    assert True
```
"""

    cleaned = generator._clean_code_response(raw)

    assert "```" not in cleaned

    assert "def test_sample" in cleaned

# ==========================================================

# VALID PYTHON

# ==========================================================

def test_valid_python_code():

    generator = LLMTestGenerator()

    code = """
def test_ok():
    assert True
"""

    assert (
        generator._is_valid_python(code)
        is True
    )

def test_invalid_python_code():

    generator = LLMTestGenerator()

    code = """
def test_fail(
"""

    assert (
        generator._is_valid_python(code)
        is False
    )

# ==========================================================

# COMPLETE TEST CODE

def test_complete_test_code():

    generator = LLMTestGenerator()

    code = """
import pytest

def test_example():
    assert True
"""

    assert (
        generator._is_complete_test_code(
            code,
            "python"
        )
        is True
    )

def test_incomplete_test_code():

    generator = LLMTestGenerator()

    code = """
def test_example():
    assert
"""

    assert (
        generator._is_complete_test_code(
            code,
            "python"
        )
        is False
    )

# ==========================================================

# REPAIR TRUNCATED PYTHON

# ==========================================================

def test_repair_truncated_python():

    generator = LLMTestGenerator()

    broken = """
import pytest

def test_example():
    with pytest.raises(ValueError)
"""

    repaired = (
        generator._repair_truncated_python(
            broken
        )
    )

    assert ":" in repaired

    assert "pass" in repaired

# ==========================================================

# DEMO TEST GENERATION

# ==========================================================

def test_generate_demo_tests_python():

    generator = LLMTestGenerator()

    tests = (
        generator._generate_demo_tests(
            "add",
            "python",
            "comprehensive"
        )
    )

    assert len(tests) > 0

    assert (
        tests[0]["language"]
        == "python"
    )

    assert (
        "def test_add"
        in tests[0]["content"]
    )

def test_generate_demo_tests_javascript():

    generator = LLMTestGenerator()

    tests = (
        generator._generate_demo_tests(
            "sum",
            "javascript",
            "comprehensive"
        )
    )

    assert len(tests) > 0

    assert (
        tests[0]["language"]
        == "javascript"
    )

    assert (
        "describe"
        in tests[0]["content"]
    )

# ==========================================================

# PROMPT CREATION

# ==========================================================

def test_create_test_generation_prompt():

    generator = LLMTestGenerator()

    prompt = (
        generator._create_test_generation_prompt(
            "def add(a, b): return a+b",
            "add",
            "python"
        )
    )

    assert "pytest" in prompt

    assert "add" in prompt

    assert "temp_code" in prompt

# ==========================================================

# EDGE CASE PROMPT

# ==========================================================

def test_create_edge_case_prompt():

    generator = LLMTestGenerator()

    edge_cases = [
        {
            "type": "null_input",
            "description": "None input"
        }
    ]

    prompt = (
        generator._create_edge_case_prompt(
            "def add(a, b): return a+b",
            "add",
            edge_cases,
            "python"
        )
    )

    assert "Edge Cases" in prompt

    assert "None input" in prompt

# ==========================================================

# FALLBACK GENERATION

# ==========================================================

def test_fallback_generation_without_api_key():

    generator = LLMTestGenerator()

    generator.has_valid_key = False

    tests = (
        generator.generate_tests_from_code(
            "def add(a,b): return a+b",
            "add",
            "python"
        )
    )

    assert len(tests) > 0

    assert (
        tests[0]["generated_by"]
        == "demo"
    )
