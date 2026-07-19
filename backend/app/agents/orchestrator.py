"""Test-generation pipeline.

Every job runs inside its own :class:`tempfile.TemporaryDirectory`, so
concurrent jobs never share state and all scratch files are cleaned up
automatically. Generated tests are executed exactly once, and coverage is
collected from that same run. Progress is reported through an ``on_stage``
callback so the frontend can show live status.
"""

import ast
import logging
import os
import re
import subprocess
import tempfile
import urllib.parse
from typing import Any, Callable, Dict, List, Optional

from app.agents.edge_case_finder import EdgeCaseFinderAgent
from app.agents.llm_test_generator import LLMTestGenerator
from app.agents.repo_scanner import RepoScannerAgent
from app.core.config import settings

logger = logging.getLogger(__name__)

MODULE_NAME = "temp_code"
PYTEST_TIMEOUT = 90
_ALLOWED_GIT_HOSTS = {"github.com", "gitlab.com", "bitbucket.org"}

StageCallback = Callable[[str], None]


class TestGenerationOrchestrator:
    def __init__(self, on_stage: Optional[StageCallback] = None) -> None:
        self.edge_case_finder = EdgeCaseFinderAgent()
        self.llm = LLMTestGenerator()
        self._on_stage = on_stage

    def _stage(self, stage: str) -> None:
        if self._on_stage:
            try:
                self._on_stage(stage)
            except Exception:  # noqa: BLE001 - progress reporting is best-effort
                pass

    # ------------------------------------------------------------------
    # Public entry points
    # ------------------------------------------------------------------
    def analyze_from_text(self, source_code: str, language: str = "python") -> Dict[str, Any]:
        self._stage("extracting_functions")
        with tempfile.TemporaryDirectory(prefix="atcg_") as workdir:
            self._write_module(workdir, source_code)
            functions = self._extract_python_functions(source_code, f"{MODULE_NAME}.py")
            return self._run_pipeline(
                workdir, source_code, functions, {"python": 1}, files_scanned=1
            )

    def analyze_from_zip(self, zip_path: str) -> Dict[str, Any]:
        self._stage("scanning")
        with tempfile.TemporaryDirectory(prefix="atcg_zip_") as extract_dir:
            RepoScannerAgent.extract_from_zip(zip_path, extract_dir)
            return self._analyze_repository(extract_dir)

    def analyze_from_url(self, github_url: str) -> Dict[str, Any]:
        self._validate_repo_url(github_url)
        self._stage("scanning")
        with tempfile.TemporaryDirectory(prefix="atcg_clone_") as clone_dir:
            RepoScannerAgent.clone_from_github(github_url, clone_dir)
            return self._analyze_repository(clone_dir)

    # ------------------------------------------------------------------
    # Repository analysis (zip / clone)
    # ------------------------------------------------------------------
    def _analyze_repository(self, repo_path: str) -> Dict[str, Any]:
        structure = RepoScannerAgent(repo_path).scan()
        source_files = [
            path
            for path in structure.get("files", [])
            if path.endswith((".py", ".js", ".ts"))
        ][: settings.max_files_to_analyze]

        self._stage("extracting_functions")
        combined_source = ""
        functions: List[Dict[str, Any]] = []
        for rel_path in source_files:
            try:
                with open(os.path.join(repo_path, rel_path), "r", encoding="utf-8", errors="ignore") as handle:
                    content = handle.read()
            except OSError as exc:
                logger.warning("Could not read %s: %s", rel_path, exc)
                continue
            if len(content) > 50_000:
                continue
            combined_source += "\n\n" + content
            if rel_path.endswith(".py"):
                functions.extend(self._extract_python_functions(content, rel_path))

        with tempfile.TemporaryDirectory(prefix="atcg_") as workdir:
            self._write_module(workdir, combined_source)
            return self._run_pipeline(
                workdir,
                combined_source,
                functions,
                structure.get("languages", {}),
                files_scanned=structure.get("total_files", len(source_files)),
            )

    # ------------------------------------------------------------------
    # Shared pipeline
    # ------------------------------------------------------------------
    def _run_pipeline(
        self,
        workdir: str,
        source_code: str,
        functions: List[Dict[str, Any]],
        languages: Dict[str, int],
        files_scanned: int,
    ) -> Dict[str, Any]:
        total_discovered = len(functions)
        functions = functions[: settings.max_functions_to_analyze]

        self._stage("finding_edge_cases")
        edge_cases = self._collect_edge_cases(functions)

        self._stage("generating_tests")
        generated_tests, test_files = self._generate_tests(workdir, functions)

        self._stage("running_tests")
        test_results, coverage = self._execute_tests(workdir, test_files)

        total_test_cases = sum(
            len(re.findall(r"^\s*def test_", t["content"], re.MULTILINE))
            for t in generated_tests
        )

        return {
            "structure": {
                "languages": languages,
                "functions": [{"name": f["name"], "file": f["file"]} for f in functions],
            },
            "stats": {
                "files_scanned": files_scanned,
                "total_loc": source_code.count("\n") + 1 if source_code.strip() else 0,
                "functions_found": total_discovered,
                "functions_analyzed": len(functions),
                "test_modules": len(generated_tests),
                "test_cases": total_test_cases,
            },
            "edge_cases": edge_cases[:20],
            "tests": generated_tests,
            "test_results": test_results,
            "coverage": coverage,
            "llm_provider": settings.llm_provider,
        }

    def _collect_edge_cases(self, functions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        edge_cases: List[Dict[str, Any]] = []
        for fn in functions:
            info = {
                "name": fn["name"],
                "args": fn.get("args", []),
                "source_code": fn.get("context", ""),
                "docstring": fn.get("context", ""),
            }
            try:
                edge_cases.extend(self.edge_case_finder.find_edge_cases(info, "")[:10])
            except Exception as exc:  # noqa: BLE001
                logger.warning("Edge-case detection failed for %s: %s", fn["name"], exc)

        seen: set[tuple] = set()
        unique: List[Dict[str, Any]] = []
        for case in edge_cases:
            key = (case.get("type"), case.get("description"))
            if key in seen:
                continue
            seen.add(key)
            unique.append(case)
        return unique

    def _generate_tests(
        self, workdir: str, functions: List[Dict[str, Any]]
    ) -> tuple[List[Dict[str, Any]], List[str]]:
        py_functions = [f for f in functions if f.get("language") == "python"]
        raw = self.llm.generate_tests(py_functions)  # {name: code}

        generated: List[Dict[str, Any]] = []
        test_files: List[str] = []
        for index, fn in enumerate(py_functions):
            code = raw.get(fn["name"])
            if not code:
                continue
            content = self._fix_test_imports(code, fn["name"])
            if not self._is_valid_python(content):
                continue
            file_name = f"test_{fn['name']}_{index}.py"
            with open(os.path.join(workdir, file_name), "w", encoding="utf-8") as handle:
                handle.write(content)
            generated.append(
                {
                    "target_function": fn["name"],
                    "test_type": "comprehensive",
                    "language": "python",
                    "content": content,
                }
            )
            test_files.append(file_name)
        return generated, test_files

    def _execute_tests(
        self, workdir: str, test_files: List[str]
    ) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        if not test_files:
            return [], self._empty_coverage()

        self._stage("computing_coverage")
        coverage_path = os.path.join(workdir, "coverage.json")
        env = os.environ.copy()
        env["PYTHONPATH"] = workdir
        try:
            process = subprocess.run(
                [
                    "python", "-m", "pytest", *test_files,
                    "-v", "--tb=short", "-p", "no:cacheprovider",
                    f"--cov={MODULE_NAME}", f"--cov-report=json:{coverage_path}",
                ],
                cwd=workdir, env=env, capture_output=True, text=True, timeout=PYTEST_TIMEOUT,
            )
            output = process.stdout + "\n" + process.stderr
        except subprocess.TimeoutExpired:
            return (
                [{"file": "generated tests", "status": "timeout", "output": "Execution timed out"}],
                self._empty_coverage(),
            )
        return self._parse_pytest_output(output, test_files), self._parse_coverage(coverage_path)

    # ------------------------------------------------------------------
    # Parsing / helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _write_module(workdir: str, source_code: str) -> None:
        with open(os.path.join(workdir, f"{MODULE_NAME}.py"), "w", encoding="utf-8") as handle:
            handle.write(source_code)

    @staticmethod
    def _empty_coverage() -> Dict[str, Any]:
        return {"total_coverage": 0.0, "covered_lines": 0, "total_lines": 0, "executed": False}

    @staticmethod
    def _parse_pytest_output(output: str, test_files: List[str]) -> List[Dict[str, Any]]:
        results = []
        for file_name in test_files:
            file_lines = [ln for ln in output.splitlines() if file_name in ln and "::" in ln]
            failed = any("FAILED" in ln or "ERROR" in ln for ln in file_lines)
            passed = any("PASSED" in ln for ln in file_lines)
            status = "failed" if failed else ("passed" if passed else "no tests")
            results.append({"file": file_name, "status": status, "output": "\n".join(file_lines)})
        return results

    @staticmethod
    def _parse_coverage(coverage_path: str) -> Dict[str, Any]:
        empty = {"total_coverage": 0.0, "covered_lines": 0, "total_lines": 0, "executed": False}
        if not os.path.exists(coverage_path):
            return empty
        try:
            import json

            with open(coverage_path, "r", encoding="utf-8") as handle:
                totals = json.load(handle).get("totals", {})
            return {
                "total_coverage": round(totals.get("percent_covered", 0.0), 2),
                "covered_lines": totals.get("covered_lines", 0),
                "total_lines": totals.get("num_statements", 0),
                "executed": totals.get("num_statements", 0) > 0,
            }
        except (OSError, ValueError) as exc:
            logger.warning("Coverage parse failed: %s", exc)
            return empty

    @staticmethod
    def _validate_repo_url(url: str) -> None:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            raise ValueError("Only http(s) repository URLs are allowed")
        if parsed.hostname not in _ALLOWED_GIT_HOSTS:
            raise ValueError(f"Repository host '{parsed.hostname}' is not allowed")

    @staticmethod
    def _extract_python_functions(source_code: str, file_name: str) -> List[Dict[str, Any]]:
        functions: List[Dict[str, Any]] = []
        try:
            tree = ast.parse(source_code)
        except SyntaxError as exc:
            logger.warning("Could not parse %s: %s", file_name, exc)
            return functions

        lines = source_code.splitlines()
        # Top-level functions only: generated tests import by name, so class
        # methods and dunders cannot be imported standalone.
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if node.name.startswith("__"):
                continue
            end = getattr(node, "end_lineno", node.lineno + 20)
            functions.append(
                {
                    "name": node.name,
                    "file": file_name,
                    "language": "python",
                    "args": [{"name": a.arg} for a in node.args.args if a.arg != "self"],
                    "context": "\n".join(lines[node.lineno - 1 : end]),
                }
            )
        return functions

    @staticmethod
    def _fix_test_imports(test_content: str, function_name: str) -> str:
        header = (
            "import sys, os\n"
            "sys.path.insert(0, os.path.dirname(__file__))\n"
            "import pytest\n"
            f"from {MODULE_NAME} import {function_name}\n\n"
        )
        skip = ("import pytest", "import sys", "import os", "sys.path")
        body_lines = []
        for line in test_content.strip().splitlines():
            stripped = line.strip()
            if any(stripped.startswith(prefix) for prefix in skip):
                continue
            if stripped.startswith("from temp_code import"):
                continue
            body_lines.append(line)

        body = "\n".join(body_lines)
        for pattern in (r"from your_module import", r"from module import", r"import your_module"):
            body = re.sub(pattern, f"from {MODULE_NAME} import", body)
        return (header + body).strip()

    @staticmethod
    def _is_valid_python(code: str) -> bool:
        try:
            ast.parse(code)
        except SyntaxError:
            return False
        return "test_" in code
