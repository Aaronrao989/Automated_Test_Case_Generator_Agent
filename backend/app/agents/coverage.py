import json
import os
import subprocess

from typing import Dict, List, Any


class CoverageAgent:
    """
    Computes and analyzes code coverage.

    Features:
    - Python coverage using coverage.py
    - JavaScript coverage using Jest
    - File-wise coverage
    - Uncovered code analysis
    - Missing scenario suggestions
    """

    def __init__(self):

        pass

    # ==========================================================
    # MAIN ENTRY
    # ==========================================================

    def compute_coverage(
        self,
        test_results: List[Dict[str, Any]],
        source_files: List[str],
        language: str = "python"
    ) -> Dict[str, Any]:

        if language == "python":

            return self._compute_python_coverage(
                source_files
            )

        elif language == "javascript":

            return self._compute_js_coverage(
                source_files
            )

        return {
            "total_coverage": 0,
            "covered_lines": 0,
            "total_lines": 0,
            "file_coverage": {},
            "uncovered_code": [],
            "error": "Unsupported language"
        }

    # ==========================================================
    # PYTHON COVERAGE
    # ==========================================================

    def _compute_python_coverage(
        self,
        source_files: List[str]
    ) -> Dict[str, Any]:

        try:

            print("[Coverage] Running Python coverage")

            # --------------------------------------------------
            # CLEAN OLD FILES
            # --------------------------------------------------

            if os.path.exists(".coverage"):

                os.remove(".coverage")

            if os.path.exists("coverage.json"):

                os.remove("coverage.json")

            # --------------------------------------------------
            # DETERMINE SOURCE ROOTS
            # --------------------------------------------------

            source_dirs = set()

            for file_path in source_files:

                abs_path = os.path.abspath(file_path)

                source_dirs.add(
                    os.path.dirname(abs_path)
                )

            source_arg = ",".join(source_dirs)

            if not source_arg:

                source_arg = "."

            # --------------------------------------------------
            # RUN COVERAGE
            # --------------------------------------------------

            run_result = subprocess.run(
                [
                    "python",
                    "-m",
                    "coverage",
                    "run",
                    f"--source={source_arg}",
                    "-m",
                    "pytest",
                    "generated_tests",
                    "-v"
                ],
                capture_output=True,
                text=True,
                timeout=120
            )

            # --------------------------------------------------
            # GENERATE JSON
            # --------------------------------------------------

            json_result = subprocess.run(
                [
                    "python",
                    "-m",
                    "coverage",
                    "json",
                    "-o",
                    "coverage.json"
                ],
                capture_output=True,
                text=True,
                timeout=60
            )

            if json_result.returncode != 0:

                return {
                    "total_coverage": 0,
                    "covered_lines": 0,
                    "total_lines": 0,
                    "file_coverage": {},
                    "uncovered_code": [],
                    "raw_output": run_result.stdout,
                    "raw_errors": run_result.stderr,
                    "error": json_result.stderr
                }

            if not os.path.exists("coverage.json"):

                return {
                    "total_coverage": 0,
                    "covered_lines": 0,
                    "total_lines": 0,
                    "file_coverage": {},
                    "uncovered_code": [],
                    "error": "coverage.json not generated"
                }

            # --------------------------------------------------
            # LOAD COVERAGE DATA
            # --------------------------------------------------

            with open(
                "coverage.json",
                "r",
                encoding="utf-8"
            ) as f:

                coverage_data = json.load(f)

            files_data = coverage_data.get(
                "files",
                {}
            )

            total_lines = 0
            covered_lines = 0

            file_coverage = {}

            # --------------------------------------------------
            # PARSE FILE COVERAGE
            # --------------------------------------------------

            for file_path, file_data in files_data.items():

                # Skip irrelevant files

                if (
                    "generated_tests" in file_path
                    or "__pycache__" in file_path
                    or "site-packages" in file_path
                ):

                    continue

                summary = file_data.get(
                    "summary",
                    {}
                )

                total = summary.get(
                    "num_statements",
                    0
                )

                covered = summary.get(
                    "covered_lines",
                    0
                )

                percent = summary.get(
                    "percent_covered",
                    0
                )

                if total <= 0:

                    continue

                total_lines += total

                covered_lines += covered

                file_coverage[file_path] = round(
                    percent,
                    2
                )

            # --------------------------------------------------
            # TOTAL COVERAGE
            # --------------------------------------------------

            if total_lines > 0:

                total_coverage = round(
                    (covered_lines / total_lines) * 100,
                    2
                )

            else:

                total_coverage = 0.0

            total_coverage = min(
                total_coverage,
                100.0
            )

            return {
                "total_coverage": total_coverage,
                "covered_lines": covered_lines,
                "total_lines": total_lines,
                "file_coverage": file_coverage,
                "uncovered_code": self._identify_uncovered_code(
                    source_files
                ),
                "raw_output": run_result.stdout,
                "raw_errors": run_result.stderr
            }

        except subprocess.TimeoutExpired:

            return {
                "total_coverage": 0,
                "covered_lines": 0,
                "total_lines": 0,
                "file_coverage": {},
                "uncovered_code": [],
                "error": "Coverage execution timed out"
            }

        except Exception as e:

            return {
                "total_coverage": 0,
                "covered_lines": 0,
                "total_lines": 0,
                "file_coverage": {},
                "uncovered_code": [],
                "error": str(e)
            }

    # ==========================================================
    # JAVASCRIPT COVERAGE
    # ==========================================================

    def _compute_js_coverage(
        self,
        source_files: List[str]
    ) -> Dict[str, Any]:

        try:

            print("[Coverage] Running Jest coverage")

            result = subprocess.run(
                [
                    "npx",
                    "jest",
                    "--coverage",
                    "--coverageReporters=json"
                ],
                capture_output=True,
                text=True,
                timeout=120
            )

            coverage_file = (
                "coverage/coverage-final.json"
            )

            if not os.path.exists(coverage_file):

                return {
                    "total_coverage": 0,
                    "covered_lines": 0,
                    "total_lines": 0,
                    "file_coverage": {},
                    "uncovered_code": [],
                    "error": "coverage-final.json not found"
                }

            with open(
                coverage_file,
                "r",
                encoding="utf-8"
            ) as f:

                coverage_data = json.load(f)

            total_lines = 0
            covered_lines = 0

            file_coverage = {}

            for file_path, file_data in coverage_data.items():

                lines_data = file_data.get(
                    "s",
                    {}
                )

                total = len(lines_data)

                covered = sum(
                    1
                    for value in lines_data.values()
                    if value > 0
                )

                if total <= 0:

                    continue

                percent = round(
                    (covered / total) * 100,
                    2
                )

                file_coverage[file_path] = percent

                total_lines += total

                covered_lines += covered

            if total_lines > 0:

                total_coverage = round(
                    (covered_lines / total_lines) * 100,
                    2
                )

            else:

                total_coverage = 0.0

            total_coverage = min(
                total_coverage,
                100.0
            )

            return {
                "total_coverage": total_coverage,
                "covered_lines": covered_lines,
                "total_lines": total_lines,
                "file_coverage": file_coverage,
                "uncovered_code": self._identify_uncovered_code(
                    source_files
                ),
                "raw_output": result.stdout,
                "raw_errors": result.stderr
            }

        except subprocess.TimeoutExpired:

            return {
                "total_coverage": 0,
                "covered_lines": 0,
                "total_lines": 0,
                "file_coverage": {},
                "uncovered_code": [],
                "error": "Jest coverage timed out"
            }

        except Exception as e:

            return {
                "total_coverage": 0,
                "covered_lines": 0,
                "total_lines": 0,
                "file_coverage": {},
                "uncovered_code": [],
                "error": str(e)
            }

    # ==========================================================
    # UNCOVERED CODE ANALYSIS
    # ==========================================================

    def _identify_uncovered_code(
        self,
        source_files: List[str]
    ) -> List[Dict[str, Any]]:

        uncovered = []

        keywords = [
            "def ",
            "class ",
            "if ",
            "for ",
            "while ",
            "return",
            "raise",
            "except",
            "try"
        ]

        for file_path in source_files:

            try:

                if not os.path.exists(file_path):

                    continue

                with open(
                    file_path,
                    "r",
                    encoding="utf-8",
                    errors="ignore"
                ) as f:

                    lines = f.readlines()

                for i, line in enumerate(lines):

                    stripped = line.strip()

                    if not stripped:

                        continue

                    if any(
                        keyword in stripped.lower()
                        for keyword in keywords
                    ):

                        uncovered.append({
                            "file": file_path,
                            "line": i + 1,
                            "code": stripped[:300],
                            "importance": self._assess_importance(
                                stripped
                            )
                        })

            except Exception as e:

                print(
                    f"[Coverage] Failed reading "
                    f"{file_path}: {e}"
                )

        uncovered.sort(
            key=lambda x: x["importance"],
            reverse=True
        )

        return uncovered[:20]

    # ==========================================================
    # IMPORTANCE SCORE
    # ==========================================================

    def _assess_importance(
        self,
        code_line: str
    ) -> int:

        importance = 0

        keyword_scores = {
            "class": 5,
            "def": 4,
            "raise": 4,
            "except": 3,
            "try": 2,
            "if": 2,
            "for": 2,
            "while": 2,
            "return": 1
        }

        lowered = code_line.lower()

        for keyword, score in keyword_scores.items():

            if keyword in lowered:

                importance += score

        return importance

    # ==========================================================
    # SUGGEST MISSING SCENARIOS
    # ==========================================================

    def suggest_missing_scenarios(
        self,
        coverage_report: Dict[str, Any],
        functions: List[Dict[str, Any]]
    ) -> List[str]:

        suggestions = []

        file_coverage = coverage_report.get(
            "file_coverage",
            {}
        )

        for file_path, coverage_pct in file_coverage.items():

            if coverage_pct < 50:

                suggestions.append(
                    f"File '{file_path}' has "
                    f"low coverage ({coverage_pct}%). "
                    f"Add more unit tests."
                )

        for func in functions:

            func_name = func.get(
                "name",
                ""
            ).lower()

            if (
                "error" in func_name
                or "exception" in func_name
            ):

                suggestions.append(
                    f"Function '{func_name}' "
                    f"needs exception tests."
                )

            if (
                "validate" in func_name
                or "check" in func_name
            ):

                suggestions.append(
                    f"Function '{func_name}' "
                    f"needs validation tests."
                )

            if (
                "api" in func_name
                or "request" in func_name
            ):

                suggestions.append(
                    f"Function '{func_name}' "
                    f"needs API failure tests."
                )

        return suggestions[:20]