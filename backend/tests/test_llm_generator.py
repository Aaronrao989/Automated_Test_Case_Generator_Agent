"""LLMTestGenerator tests (offline demo mode + parsing)."""

from app.agents.llm_test_generator import LLMTestGenerator


def test_demo_mode_without_key():
    gen = LLMTestGenerator()
    assert gen.has_valid_key is False
    out = gen.generate_tests([{"name": "add", "context": "def add(a,b): return a+b", "language": "python"}])
    assert "add" in out
    assert "def test_add" in out["add"]


def test_generate_tests_empty():
    assert LLMTestGenerator().generate_tests([]) == {}


def test_parse_batch_splits_by_marker():
    raw = (
        "### FUNCTION: add\n"
        "def test_add():\n    assert True\n\n"
        "### FUNCTION: sub\n"
        "def test_sub():\n    assert True\n"
    )
    parsed = LLMTestGenerator._parse_batch(raw, ["add", "sub"])
    assert "def test_add" in parsed["add"]
    assert "def test_sub" in parsed["sub"]


def test_parse_batch_single_no_marker():
    raw = "def test_only():\n    assert True\n"
    parsed = LLMTestGenerator._parse_batch(raw, ["only"])
    assert "def test_only" in parsed["only"]


def test_clean_strips_fences_and_dedupes_imports():
    raw = "```python\nimport pytest\nimport pytest\n\ndef test_x():\n    assert True\n```"
    cleaned = LLMTestGenerator._clean(raw)
    assert "```" not in cleaned
    assert cleaned.count("import pytest") == 1


def test_is_valid_python():
    assert LLMTestGenerator._is_valid_python("def test_x():\n    assert True\n")
    assert not LLMTestGenerator._is_valid_python("x = 1")  # no test_
    assert not LLMTestGenerator._is_valid_python("def test_x(:\n")  # syntax error
