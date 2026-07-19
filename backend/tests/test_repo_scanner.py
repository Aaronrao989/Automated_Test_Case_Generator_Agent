"""RepoScannerAgent tests."""

import os
import zipfile

from app.agents.repo_scanner import RepoScannerAgent


def test_scan_detects_languages(tmp_path):
    (tmp_path / "a.py").write_text("def f():\n    return 1\n")
    (tmp_path / "b.js").write_text("function g() { return 1; }\n")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "skip.py").write_text("x = 1\n")

    result = RepoScannerAgent(str(tmp_path)).scan()
    assert result["languages"].get("python") == 1
    assert result["languages"].get("javascript") == 1
    # ignored directories are skipped
    assert all("node_modules" not in f for f in result["files"])


def test_scan_missing_path():
    result = RepoScannerAgent("/does/not/exist").scan()
    assert result["total_files"] == 0


def test_extract_from_zip_skips_traversal(tmp_path):
    zip_path = tmp_path / "repo.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("good.py", "x = 1\n")
        archive.writestr("../evil.py", "x = 2\n")

    out = tmp_path / "out"
    out.mkdir()
    RepoScannerAgent.extract_from_zip(str(zip_path), str(out))
    assert os.path.exists(out / "good.py")
    # traversal member must not escape the extraction dir
    assert not os.path.exists(tmp_path / "evil.py")
