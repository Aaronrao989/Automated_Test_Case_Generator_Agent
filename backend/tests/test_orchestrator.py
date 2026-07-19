"""Orchestrator unit tests."""

import pytest

from app.agents.orchestrator import TestGenerationOrchestrator


@pytest.fixture()
def orch():
    return TestGenerationOrchestrator()


def test_extract_top_level_functions_only(orch):
    code = "def add(a, b):\n    return a + b\n\nclass C:\n    def m(self, x):\n        return x\n"
    names = {f["name"] for f in orch._extract_python_functions(code, "m.py")}
    assert "add" in names
    assert "m" not in names  # class methods excluded


def test_extract_skips_dunders(orch):
    code = "def __init__(self):\n    pass\n\ndef real(x):\n    return x\n"
    names = {f["name"] for f in orch._extract_python_functions(code, "m.py")}
    assert names == {"real"}


def test_fix_test_imports_normalizes(orch):
    raw = "import pytest\nfrom module import add\n\ndef test_add():\n    assert add(1, 2) == 3\n"
    fixed = orch._fix_test_imports(raw, "add")
    assert "from temp_code import add" in fixed
    assert "from module import add" not in fixed


def test_parse_pytest_output(orch):
    output = "test_add_0.py::test_add PASSED\ntest_div_1.py::test_div FAILED\n"
    results = {r["file"]: r["status"] for r in orch._parse_pytest_output(output, ["test_add_0.py", "test_div_1.py"])}
    assert results["test_add_0.py"] == "passed"
    assert results["test_div_1.py"] == "failed"


def test_validate_repo_url(orch):
    with pytest.raises(ValueError):
        orch._validate_repo_url("file:///etc/passwd")
    with pytest.raises(ValueError):
        orch._validate_repo_url("https://evil.example.com/x.git")
    orch._validate_repo_url("https://github.com/user/repo")  # allowed


def test_analyze_from_text_demo_mode(orch):
    stages = []
    orch._on_stage = stages.append
    result = orch.analyze_from_text("def add(a, b):\n    return a + b\n")
    assert result["structure"]["functions"][0]["name"] == "add"
    assert result["stats"]["functions_analyzed"] == 1
    assert "coverage" in result
    assert "generating_tests" in stages and "running_tests" in stages
