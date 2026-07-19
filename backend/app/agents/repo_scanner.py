"""Repository scanning: file tree, language detection, and safe ingestion."""

import logging
import os
import subprocess
import zipfile
from collections import defaultdict
from typing import Any, Dict

logger = logging.getLogger(__name__)


class RepoScannerAgent:
    LANGUAGE_EXTENSIONS = {
        "python": [".py"],
        "javascript": [".js", ".jsx", ".ts", ".tsx"],
        "java": [".java"],
        "cpp": [".cpp", ".cc", ".h"],
        "go": [".go"],
        "rust": [".rs"],
    }
    IGNORE_DIRS = {
        ".git", "node_modules", "__pycache__", ".venv", "venv", "env",
        "dist", "build", ".idea", ".pytest_cache", "coverage", ".next",
        ".turbo", ".cache",
    }
    MAX_FILE_SIZE = 2 * 1024 * 1024

    def __init__(self, repo_path: str) -> None:
        self.repo_path = os.path.abspath(repo_path)
        self.files: list[str] = []
        self.language_stats: dict[str, int] = defaultdict(int)

    def scan(self) -> Dict[str, Any]:
        self.files = []
        self.language_stats.clear()
        if not os.path.exists(self.repo_path):
            return {"languages": {}, "files": [], "total_files": 0}

        self._walk(self.repo_path)
        self._detect_languages()
        unique = sorted(set(self.files))
        return {
            "languages": dict(self.language_stats),
            "files": unique,
            "total_files": len(unique),
        }

    def _walk(self, path: str, relative: str = "") -> None:
        try:
            items = sorted(os.listdir(path))
        except OSError:
            return

        for item in items:
            if item.startswith(".") or item in self.IGNORE_DIRS:
                continue
            item_path = os.path.join(path, item)
            if os.path.islink(item_path):
                continue
            rel = f"{relative}/{item}" if relative else item

            if os.path.isdir(item_path):
                self._walk(item_path, rel)
            elif os.path.isfile(item_path):
                try:
                    size = os.path.getsize(item_path)
                except OSError:
                    continue
                if 0 < size <= self.MAX_FILE_SIZE and not self._is_binary(item_path):
                    self.files.append(rel)

    @staticmethod
    def _is_binary(file_path: str) -> bool:
        try:
            with open(file_path, "rb") as handle:
                return b"\0" in handle.read(1024)
        except OSError:
            return True

    def _detect_languages(self) -> None:
        for file_path in self.files:
            ext = os.path.splitext(file_path)[1].lower()
            for language, extensions in self.LANGUAGE_EXTENSIONS.items():
                if ext in extensions:
                    self.language_stats[language] += 1
                    break

    @staticmethod
    def extract_from_zip(zip_path: str, extract_to: str) -> str:
        """Extract a zip, skipping path-traversal ('zip slip') members."""
        with zipfile.ZipFile(zip_path, "r") as archive:
            for member in archive.namelist():
                normalized = os.path.normpath(member)
                if normalized.startswith("..") or os.path.isabs(normalized):
                    continue
                archive.extract(member, extract_to)
        return extract_to

    @staticmethod
    def clone_from_github(repo_url: str, clone_to: str) -> str:
        env = os.environ.copy()
        # Restrict git to https so a crafted URL can't reach file:// or ssh://.
        env["GIT_ALLOW_PROTOCOL"] = "https"
        result = subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, clone_to],
            capture_output=True, text=True, timeout=120, env=env,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Git clone failed: {result.stderr.strip()}")
        return clone_to
