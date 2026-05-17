import logging
import uuid
from typing import Dict, Any, List, Optional

from sqlalchemy.orm import Session

from app.models import (
    AnalysisJob,
    JobStatus,
    GeneratedTest,
    EdgeCase,
    CoverageReport,
    TestExecutionResult
)


logger = logging.getLogger(__name__)


# ==========================================================
# PERSISTENCE SERVICE
# ==========================================================

class ResultsPersistenceService:
    """
    Handles persistence of analysis results to the database.
    Saves all analysis outputs: tests, edge cases, coverage, 
    test results.
    """

    def __init__(
        self,
        db: Session,
        job_id: str
    ):
        self.db = db
        self.job_id = job_id

    # ==========================================================
    # PERSIST GENERATED TESTS
    # ==========================================================

    def persist_generated_tests(
        self,
        tests: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Save generated test records to database.
        
        Args:
            tests: List of test dicts from orchestrator
                  Each test contains:
                  - content: test code
                  - target_function: function being tested
                  - language: programming language
                  - (optional) file_path
        
        Returns:
            List of persisted test IDs
        """

        test_ids = []

        try:

            for test in tests:

                test_id = str(uuid.uuid4())

                generated_test = GeneratedTest(
                    id=test_id,
                    job_id=self.job_id,
                    test_type="unit",
                    file_path=test.get(
                        "file_path",
                        f"generated_test_{test_id}.py"
                    ),
                    content=test.get("content", ""),
                    language=test.get(
                        "language",
                        "python"
                    ),
                    target_function=test.get(
                        "target_function",
                        "unknown"
                    )
                )

                self.db.add(generated_test)

                test_ids.append(test_id)

                logger.debug(
                    f"[Job {self.job_id}] "
                    f"Queued test: {test_id} "
                    f"for {test.get('target_function')}"
                )

            self.db.flush()

            logger.info(
                f"[Job {self.job_id}] "
                f"Persisted {len(test_ids)} tests"
            )

            return test_ids

        except Exception as e:

            logger.error(
                f"[Job {self.job_id}] "
                f"Failed to persist tests: {e}"
            )

            raise

    # ==========================================================
    # PERSIST EDGE CASES
    # ==========================================================

    def persist_edge_cases(
        self,
        edge_cases: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Save edge case records to database.
        
        Args:
            edge_cases: List of edge case dicts
                       Each contains:
                       - description: edge case description
                       - (optional) edge_case_type
                       - (optional) function_name
                       - (optional) suggested_test
        
        Returns:
            List of persisted edge case IDs
        """

        case_ids = []

        try:

            for edge_case in edge_cases:

                case_id = str(uuid.uuid4())

                edge_case_record = EdgeCase(
                    id=case_id,
                    job_id=self.job_id,
                    function_name=edge_case.get(
                        "function_name",
                        "unknown"
                    ),
                    edge_case_type=edge_case.get(
                        "edge_case_type",
                        "general"
                    ),
                    description=edge_case.get(
                        "description",
                        ""
                    ),
                    suggested_test=edge_case.get(
                        "suggested_test",
                        None
                    )
                )

                self.db.add(edge_case_record)

                case_ids.append(case_id)

                logger.debug(
                    f"[Job {self.job_id}] "
                    f"Queued edge case: {case_id}"
                )

            self.db.flush()

            logger.info(
                f"[Job {self.job_id}] "
                f"Persisted {len(case_ids)} edge cases"
            )

            return case_ids

        except Exception as e:

            logger.error(
                f"[Job {self.job_id}] "
                f"Failed to persist edge cases: {e}"
            )

            raise

    # ==========================================================
    # PERSIST COVERAGE REPORT
    # ==========================================================

    def persist_coverage_report(
        self,
        coverage_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Save coverage report to database.
        
        Args:
            coverage_data: Coverage report dict containing:
                          - total_coverage: float (0-100)
                          - covered_lines: int
                          - total_lines: int
                          - file_coverage: dict
                          - uncovered_code: dict (optional)
        
        Returns:
            Persisted coverage report ID or None
        """

        try:

            if not coverage_data:

                logger.warning(
                    f"[Job {self.job_id}] "
                    f"No coverage data to persist"
                )

                return None

            report_id = str(uuid.uuid4())

            coverage_report = CoverageReport(
                id=report_id,
                job_id=self.job_id,
                total_coverage=coverage_data.get(
                    "total_coverage",
                    0.0
                ),
                covered_lines=coverage_data.get(
                    "covered_lines",
                    0
                ),
                total_lines=coverage_data.get(
                    "total_lines",
                    0
                ),
                file_coverage=coverage_data.get(
                    "file_coverage",
                    {}
                ),
                uncovered_code=coverage_data.get(
                    "uncovered_code",
                    {}
                )
            )

            self.db.add(coverage_report)

            self.db.flush()

            logger.info(
                f"[Job {self.job_id}] "
                f"Persisted coverage report: "
                f"{report_id}"
            )

            return report_id

        except Exception as e:

            logger.error(
                f"[Job {self.job_id}] "
                f"Failed to persist coverage: {e}"
            )

            raise

    # ==========================================================
    # PERSIST TEST EXECUTION RESULTS
    # ==========================================================

    def persist_test_execution_results(
        self,
        test_results: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Save test execution results to database.
        
        Args:
            test_results: List of test result dicts
                         Each contains:
                         - status: pass/fail/error
                         - duration: float (seconds)
                         - output: test output (optional)
                         - error: error message (optional)
                         - (optional) test_id
        
        Returns:
            List of persisted result IDs
        """

        result_ids = []

        try:

            for i, test_result in enumerate(test_results):

                result_id = str(uuid.uuid4())

                execution_result = TestExecutionResult(
                    id=result_id,
                    job_id=self.job_id,
                    test_id=test_result.get(
                        "test_id",
                        f"test_{i}"
                    ),
                    status=test_result.get(
                        "status",
                        "unknown"
                    ),
                    duration=float(
                        test_result.get(
                            "duration",
                            0.0
                        )
                    ),
                    output=test_result.get(
                        "output",
                        None
                    ),
                    error=test_result.get(
                        "error",
                        None
                    )
                )

                self.db.add(execution_result)

                result_ids.append(result_id)

                logger.debug(
                    f"[Job {self.job_id}] "
                    f"Queued test result: {result_id} "
                    f"({test_result.get('status')})"
                )

            self.db.flush()

            logger.info(
                f"[Job {self.job_id}] "
                f"Persisted {len(result_ids)} "
                f"test execution results"
            )

            return result_ids

        except Exception as e:

            logger.error(
                f"[Job {self.job_id}] "
                f"Failed to persist test results: {e}"
            )

            raise

    # ==========================================================
    # PERSIST ALL RESULTS
    # ==========================================================

    def persist_all_results(
        self,
        analysis_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Persist all analysis results in a single transaction.
        
        Args:
            analysis_result: Complete result dict from orchestrator
                            Contains: tests, edge_cases, coverage, 
                                     test_results, etc.
        
        Returns:
            Summary dict with persisted IDs and counts
        
        Raises:
            Exception: On persistence failure (rolled back)
        """

        persistence_summary = {
            "test_ids": [],
            "edge_case_ids": [],
            "coverage_report_id": None,
            "test_result_ids": [],
            "totals": {
                "tests": 0,
                "edge_cases": 0,
                "test_results": 0
            }
        }

        try:

            logger.info(
                f"[Job {self.job_id}] "
                f"Starting persistence transaction"
            )

            # ====================================
            # PERSIST GENERATED TESTS
            # ====================================

            tests = analysis_result.get("tests", [])

            if tests:

                test_ids = self.persist_generated_tests(
                    tests
                )

                persistence_summary["test_ids"] = (
                    test_ids
                )

                persistence_summary["totals"]["tests"] = (
                    len(test_ids)
                )

            # ====================================
            # PERSIST EDGE CASES
            # ====================================

            edge_cases = analysis_result.get(
                "edge_cases",
                []
            )

            if edge_cases:

                case_ids = self.persist_edge_cases(
                    edge_cases
                )

                persistence_summary["edge_case_ids"] = (
                    case_ids
                )

                persistence_summary["totals"]["edge_cases"] = (
                    len(case_ids)
                )

            # ====================================
            # PERSIST COVERAGE REPORT
            # ====================================

            coverage = analysis_result.get(
                "coverage",
                {}
            )

            if coverage:

                coverage_id = (
                    self.persist_coverage_report(
                        coverage
                    )
                )

                persistence_summary[
                    "coverage_report_id"
                ] = coverage_id

            # ====================================
            # PERSIST TEST EXECUTION RESULTS
            # ====================================

            test_results = analysis_result.get(
                "test_results",
                []
            )

            if test_results:

                result_ids = (
                    self.persist_test_execution_results(
                        test_results
                    )
                )

                persistence_summary["test_result_ids"] = (
                    result_ids
                )

                persistence_summary["totals"][
                    "test_results"
                ] = len(result_ids)

            # ====================================
            # COMMIT TRANSACTION
            # ====================================

            logger.info(
                f"[Job {self.job_id}] "
                f"About to commit transaction..."
            )

            self.db.commit()

            logger.info(
                f"[Job {self.job_id}] "
                f"Commit completed."
            )

            # Expunge all to clear cache and force fresh database reads
            self.db.expunge_all()

            logger.info(
                f"[Job {self.job_id}] "
                f"Session cache cleared. Verifying..."
            )

            # Verify persistence by querying from database
            test_count = self.db.query(
                GeneratedTest
            ).filter(
                GeneratedTest.job_id == self.job_id
            ).count()

            edge_count = self.db.query(
                EdgeCase
            ).filter(
                EdgeCase.job_id == self.job_id
            ).count()

            coverage_count = self.db.query(
                CoverageReport
            ).filter(
                CoverageReport.job_id == self.job_id
            ).count()

            test_result_count = self.db.query(
                TestExecutionResult
            ).filter(
                TestExecutionResult.job_id == self.job_id
            ).count()

            logger.info(
                f"[Job {self.job_id}] "
                f"VERIFICATION - Tests: {test_count}, "
                f"Edge cases: {edge_count}, "
                f"Coverage: {coverage_count}, "
                f"Test results: {test_result_count}"
            )

            logger.info(
                f"[Job {self.job_id}] "
                f"All results persisted successfully: "
                f"{persistence_summary['totals']}"
            )

            return persistence_summary

        except Exception as e:

            self.db.rollback()

            logger.error(
                f"[Job {self.job_id}] "
                f"Persistence transaction failed: {e}"
            )

            logger.exception(e)

            raise
