import json
import logging
import os

from typing import (
    Dict,
    List,
    Any,
    Optional
)

import requests


logger = logging.getLogger(__name__)


class CIAgent:
    """
    CI/CD integration agent.

    Features:
    - GitHub PR comments
    - GitHub check runs
    - Coverage publishing
    - JSON report export
    - GitHub Actions workflow generation
    - Robust API handling
    """

    GITHUB_API = "https://api.github.com"

    def __init__(
        self,
        github_token: Optional[str] = None
    ):

        self.github_token = (
            github_token
            or os.getenv("GITHUB_TOKEN")
        )

        self.session = requests.Session()

        if self.github_token:

            self.session.headers.update({

                "Authorization":
                    f"Bearer {self.github_token}",

                "Accept":
                    "application/vnd.github+json"
            })

    # ==========================================================
    # CREATE PR COMMENT
    # ==========================================================

    def create_pr_comment(
        self,
        repo: str,
        pr_number: int,
        analysis_result: Dict[str, Any]
    ) -> bool:

        if not self.github_token:

            logger.warning(
                "[CI] Missing GitHub token"
            )

            return False

        try:

            body = self._format_analysis_comment(
                analysis_result
            )

            response = self.session.post(

                f"{self.GITHUB_API}/repos/"
                f"{repo}/issues/{pr_number}/comments",

                json={
                    "body": body
                },

                timeout=20
            )

            if response.status_code != 201:

                logger.error(
                    f"[CI] Failed PR comment: "
                    f"{response.text}"
                )

                return False

            return True

        except Exception as e:

            logger.error(
                f"[CI] PR comment failed: {e}"
            )

            return False

    # ==========================================================
    # CREATE CHECK RUN
    # ==========================================================

    def create_check_run(
        self,
        repo: str,
        commit_sha: str,
        analysis_result: Dict[str, Any]
    ) -> bool:

        if not self.github_token:

            return False

        try:

            tests = len(
                analysis_result.get(
                    "tests",
                    []
                )
            )

            edge_cases = len(
                analysis_result.get(
                    "edge_cases",
                    []
                )
            )

            coverage = (
                analysis_result
                .get("coverage", {})
                .get("total_coverage", 0)
            )

            payload = {

                "name":
                    "Automated Test Generation",

                "head_sha":
                    commit_sha,

                "status":
                    "completed",

                "conclusion":
                    "success",

                "output": {

                    "title":
                        "AI Test Generation Complete",

                    "summary":
                        (
                            f"Generated {tests} tests "
                            f"for {edge_cases} edge cases."
                        ),

                    "text":
                        (
                            f"Coverage: {coverage}%\n"
                            f"Tests Generated: {tests}\n"
                            f"Edge Cases: {edge_cases}"
                        )
                }
            }

            response = self.session.post(

                f"{self.GITHUB_API}/repos/"
                f"{repo}/check-runs",

                json=payload,

                timeout=20
            )

            if response.status_code not in [200, 201]:

                logger.error(
                    f"[CI] Check run failed: "
                    f"{response.text}"
                )

                return False

            return True

        except Exception as e:

            logger.error(
                f"[CI] Check run error: {e}"
            )

            return False

    # ==========================================================
    # EXPORT JSON REPORT
    # ==========================================================

    def export_test_report(
        self,
        analysis_result: Dict[str, Any],
        output_path: str = "test-report.json"
    ) -> bool:

        try:

            with open(
                output_path,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    analysis_result,
                    f,
                    indent=2,
                    ensure_ascii=False
                )

            return True

        except Exception as e:

            logger.error(
                f"[CI] Export failed: {e}"
            )

            return False

    # ==========================================================
    # PUBLISH COVERAGE
    # ==========================================================

    def publish_coverage_report(
        self,
        coverage_report: Dict[str, Any],
        repo: Optional[str] = None
    ) -> bool:

        try:

            total = coverage_report.get(
                "total_coverage",
                0
            )

            logger.info(
                f"[CI] Coverage: {total}%"
            )

            return True

        except Exception as e:

            logger.error(
                f"[CI] Coverage publish failed: {e}"
            )

            return False

    # ==========================================================
    # FORMAT COMMENT
    # ==========================================================

    def _format_analysis_comment(
        self,
        analysis_result: Dict[str, Any]
    ) -> str:

        structure = analysis_result.get(
            "structure",
            {}
        )

        edge_cases = analysis_result.get(
            "edge_cases",
            []
        )

        tests = analysis_result.get(
            "tests",
            []
        )

        test_results = analysis_result.get(
            "test_results",
            []
        )

        coverage = analysis_result.get(
            "coverage",
            {}
        )

        passed = sum(
            1
            for r in test_results
            if r.get("status") in [
                "PASSED",
                "passed"
            ]
        )

        failed = sum(
            1
            for r in test_results
            if r.get("status") in [
                "FAILED",
                "failed"
            ]
        )

        comment = []

        comment.append(
            "# 🤖 Automated Test Analysis\n"
        )

        # ------------------------------------------------------
        # STRUCTURE
        # ------------------------------------------------------

        comment.append(
            "## 📊 Repository Structure"
        )

        languages = structure.get(
            "languages",
            {}
        )

        comment.append(
            f"- Languages: "
            f"{', '.join(languages.keys())}"
        )

        comment.append(
            f"- Files analyzed: "
            f"{len(structure.get('files', []))}"
        )

        comment.append("")

        # ------------------------------------------------------
        # EDGE CASES
        # ------------------------------------------------------

        comment.append(
            "## ⚠️ Edge Cases"
        )

        comment.append(
            f"- Total discovered: "
            f"{len(edge_cases)}"
        )

        for case in edge_cases[:5]:

            comment.append(
                f"- {case.get('description')}"
            )

        if len(edge_cases) > 5:

            comment.append(
                f"- ... and "
                f"{len(edge_cases) - 5} more"
            )

        comment.append("")

        # ------------------------------------------------------
        # TESTS
        # ------------------------------------------------------

        comment.append(
            "## 🧪 Generated Tests"
        )

        grouped = {}

        for test in tests:

            test_type = test.get(
                "test_type",
                "unknown"
            )

            grouped[test_type] = (
                grouped.get(test_type, 0) + 1
            )

        for key, value in grouped.items():

            comment.append(
                f"- {key}: {value}"
            )

        comment.append("")

        # ------------------------------------------------------
        # EXECUTION
        # ------------------------------------------------------

        comment.append(
            "## ✅ Execution Results"
        )

        comment.append(
            f"- Passed: {passed}"
        )

        comment.append(
            f"- Failed: {failed}"
        )

        comment.append("")

        # ------------------------------------------------------
        # COVERAGE
        # ------------------------------------------------------

        comment.append(
            "## 📈 Coverage"
        )

        comment.append(
            f"- Total Coverage: "
            f"{coverage.get('total_coverage', 0)}%"
        )

        comment.append(
            f"- Covered Lines: "
            f"{coverage.get('covered_lines', 0)}"
        )

        comment.append(
            f"- Total Lines: "
            f"{coverage.get('total_lines', 0)}"
        )

        comment.append("")

        comment.append("---")

        comment.append(
            "Generated by Automated Test "
            "Case Generator Agent"
        )

        return "\n".join(comment)

    # ==========================================================
    # GITHUB ACTIONS WORKFLOW
    # ==========================================================

    def generate_github_actions_workflow(
        self,
        language: str = "python"
    ) -> str:

        if language == "python":

            return self._python_workflow()

        if language == "javascript":

            return self._javascript_workflow()

        return ""

    # ==========================================================
    # PYTHON WORKFLOW
    # ==========================================================

    def _python_workflow(self) -> str:

        return """
name: AI Test Pipeline

on:
  push:
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest

    steps:

      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run Tests
        run: |
          pytest -v

      - name: Coverage
        run: |
          coverage run -m pytest
          coverage report
"""

    # ==========================================================
    # JS WORKFLOW
    # ==========================================================

    def _javascript_workflow(self) -> str:

        return """
name: AI Test Pipeline

on:
  push:
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest

    steps:

      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: "20"

      - name: Install dependencies
        run: |
          npm install

      - name: Run Tests
        run: |
          npm test
"""