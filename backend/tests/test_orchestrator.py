"""
Tests for TestGenerationOrchestrator.
"""

import os

from app.agents.orchestrator import (
    TestGenerationOrchestrator
)


# ==========================================================
# INITIALIZATION
# ==========================================================

def test_orchestrator_initialization():

    orchestrator = (
        TestGenerationOrchestrator()
    )

    assert orchestrator is not None

    assert orchestrator.job_id is not None


# ==========================================================
# PYTHON FUNCTION EXTRACTION
# ==========================================================

def test_extract_python_functions():

    orchestrator = (
        TestGenerationOrchestrator()
    )

    source_code = """
def add(a, b):
    return a + b

class Calculator:

    def multiply(self, a, b):
        return a * b
"""

    functions = (
        orchestrator._extract_python_functions(
            source_code,
            "sample.py"
        )
    )

    assert len(functions) >= 2

    assert any(
        f["name"] == "add"
        for f in functions
    )

    assert any(
        f["name"] == "multiply"
        for f in functions
    )


# ==========================================================
# JAVASCRIPT FUNCTION EXTRACTION
# ==========================================================

def test_extract_js_functions():

    orchestrator = (
        TestGenerationOrchestrator()
    )

    source_code = """
function add(a, b) {
    return a + b;
}

const subtract = (a, b) => {
    return a - b;
};
"""

    functions = (
        orchestrator._extract_js_functions(
            source_code,
            "sample.js"
        )
    )

    assert len(functions) >= 2

    assert any(
        f["name"] == "add"
        for f in functions
    )

    assert any(
        f["name"] == "subtract"
        for f in functions
    )


# ==========================================================
# PYTHON TEST VALIDATION
# ==========================================================

def test_validate_python_test_valid():

    orchestrator = (
        TestGenerationOrchestrator()
    )

    valid_code = """
def test_example():
    assert True
"""

    assert (
        orchestrator._validate_python_test(
            valid_code
        )
        is True
    )


def test_validate_python_test_invalid():

    orchestrator = (
        TestGenerationOrchestrator()
    )

    invalid_code = """
def test_example(
"""

    assert (
        orchestrator._validate_python_test(
            invalid_code
        )
        is False
    )


# ==========================================================
# SAVE GENERATED TESTS
# ==========================================================

def test_save_generated_tests():

    orchestrator = (
        TestGenerationOrchestrator()
    )

    tests = [

        {
            "file_path":
                "tests/test_sample.py",

            "content":
                (
                    "def test_ok():\n"
                    "    assert True"
                )
        }
    ]

    saved = (
        orchestrator._save_generated_tests(
            tests
        )
    )

    assert len(saved) == 1

    assert os.path.exists(
        saved[0]
    )


# ==========================================================
# ANALYZE RAW PYTHON TEXT
# ==========================================================

def test_analyze_from_text():

    orchestrator = (
        TestGenerationOrchestrator()
    )

    source_code = """
def add(a, b):
    return a + b
"""

    result = (
        orchestrator.analyze_from_text(
            source_code,
            "python"
        )
    )

    assert isinstance(
        result,
        dict
    )

    assert (
        result["status"]
        == "COMPLETED"
    )

    assert "structure" in result


# ==========================================================
# CLEANUP GENERATED TESTS
# ==========================================================

def test_cleanup_generated_tests():

    orchestrator = (
        TestGenerationOrchestrator()
    )

    os.makedirs(
        "generated_tests",
        exist_ok=True
    )

    test_file = os.path.join(
        "generated_tests",
        "test_temp.py"
    )

    with open(
        test_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write("test")

    assert os.path.exists(
        test_file
    )

    orchestrator._cleanup_generated_tests()

    assert not os.path.exists(
        test_file
    )


# ==========================================================
# FUNCTION INFO BUILD
# ==========================================================

def test_build_function_info():

    orchestrator = (
        TestGenerationOrchestrator()
    )

    func = {

        "name": "add",

        "context":
            "def add(a, b): return a+b",

        "args": [
            {"name": "a"},
            {"name": "b"}
        ]
    }

    info = (
        orchestrator._build_function_info(
            func
        )
    )

    assert info["name"] == "add"

    assert len(info["args"]) == 2


# ==========================================================
# FIX IMPORTS
# ==========================================================

def test_fix_test_imports():

    orchestrator = (
        TestGenerationOrchestrator()
    )

    original = (
        "from your_module import add"
    )

    fixed = (
        orchestrator._fix_test_imports(
            original,
            "temp_code"
        )
    )

    assert (
        "from temp_code import add"
        in fixed
    )