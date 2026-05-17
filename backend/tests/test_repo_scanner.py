"""
Tests for RepoScannerAgent.
"""

import os
import tempfile

from app.agents.repo_scanner import (
    RepoScannerAgent
)


# ==========================================================
# INITIALIZATION
# ==========================================================

def test_repo_scanner_initialization():

    scanner = RepoScannerAgent("/tmp")

    assert scanner.repo_path == "/tmp"


# ==========================================================
# EMPTY DIRECTORY
# ==========================================================

def test_scan_empty_directory():

    with tempfile.TemporaryDirectory() as tmpdir:

        scanner = RepoScannerAgent(tmpdir)

        result = scanner.scan()

        assert "file_tree" in result

        assert "languages" in result

        assert "files" in result

        assert result["files"] == []


# ==========================================================
# PYTHON FILE DETECTION
# ==========================================================

def test_detect_python_files():

    with tempfile.TemporaryDirectory() as tmpdir:

        test_file = os.path.join(
            tmpdir,
            "test.py"
        )

        with open(
            test_file,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                "def hello():\n    pass"
            )

        scanner = RepoScannerAgent(tmpdir)

        result = scanner.scan()

        assert "python" in result["languages"]

        assert (
            result["languages"]["python"]
            == 1
        )

        assert "test.py" in result["files"]


# ==========================================================
# FUNCTION EXTRACTION
# ==========================================================

def test_extract_python_functions():

    with tempfile.TemporaryDirectory() as tmpdir:

        test_file = os.path.join(
            tmpdir,
            "test.py"
        )

        with open(
            test_file,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                """
def add(a, b):
    return a + b

class Calculator:

    def multiply(self, a, b):
        return a * b
"""
            )

        scanner = RepoScannerAgent(tmpdir)

        # IMPORTANT:
        # Must populate scanner.files
        scanner.scan()

        functions = scanner.extract_functions()

        assert len(functions) > 0

        assert any(
            f["name"] == "add"
            for f in functions
        )

        assert any(
            f["name"] == "Calculator"
            for f in functions
        )


# ==========================================================
# IGNORE HIDDEN DIRECTORIES
# ==========================================================

def test_ignore_hidden_directories():

    with tempfile.TemporaryDirectory() as tmpdir:

        hidden_dir = os.path.join(
            tmpdir,
            ".git"
        )

        os.makedirs(hidden_dir)

        hidden_file = os.path.join(
            hidden_dir,
            "config"
        )

        with open(
            hidden_file,
            "w",
            encoding="utf-8"
        ) as f:

            f.write("test")

        scanner = RepoScannerAgent(tmpdir)

        result = scanner.scan()

        assert (
            "config"
            not in result["files"]
        )


# ==========================================================
# IGNORE LARGE FILES
# ==========================================================

def test_ignore_large_files():

    with tempfile.TemporaryDirectory() as tmpdir:

        large_file = os.path.join(
            tmpdir,
            "huge.py"
        )

        with open(
            large_file,
            "wb"
        ) as f:

            f.write(
                b"x"
                * (
                    RepoScannerAgent.MAX_FILE_SIZE
                    + 1
                )
            )

        scanner = RepoScannerAgent(tmpdir)

        result = scanner.scan()

        assert (
            "huge.py"
            not in result["files"]
        )


# ==========================================================
# JAVASCRIPT DETECTION
# ==========================================================

def test_detect_javascript_files():

    with tempfile.TemporaryDirectory() as tmpdir:

        js_file = os.path.join(
            tmpdir,
            "app.js"
        )

        with open(
            js_file,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                """
function hello() {
    return "world";
}
"""
            )

        scanner = RepoScannerAgent(tmpdir)

        result = scanner.scan()

        assert (
            "javascript"
            in result["languages"]
        )

        assert (
            result["languages"]["javascript"]
            == 1
        )