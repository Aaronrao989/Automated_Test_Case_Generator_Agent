"""Tests for the CLI report builder."""

from app.cli import build_report, main


def test_build_report_renders_table_and_tests():
    results = [
        {
            "_path": "foo.py",
            "stats": {"functions_analyzed": 1, "test_cases": 3},
            "coverage": {"total_coverage": 90.0, "executed": True},
            "test_results": [{"status": "passed"}],
            "tests": [{"target_function": "foo", "content": "def test_foo():\n    assert True\n"}],
        }
    ]
    md = build_report(results)
    assert "Automated Test Generation" in md
    assert "`foo.py`" in md
    assert "100%" in md  # pass rate
    assert "90.0%" in md  # coverage
    assert "```python" in md


def test_build_report_marks_uncovered_as_not_run():
    results = [
        {
            "_path": "bar.py",
            "stats": {"functions_analyzed": 1, "test_cases": 0},
            "coverage": {"total_coverage": 0.0, "executed": False},
            "test_results": [],
            "tests": [],
        }
    ]
    assert "not run" in build_report(results)


def test_main_with_no_files_returns_zero():
    assert main([]) == 0
