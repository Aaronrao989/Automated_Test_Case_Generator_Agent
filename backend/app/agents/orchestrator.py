import uuid
import re
import ast
import os
import time
import tempfile
import subprocess

from typing import Dict, List, Any

from app.agents.repo_scanner import RepoScannerAgent
from app.agents.code_understanding import CodeUnderstandingAgent
from app.agents.edge_case_finder import EdgeCaseFinderAgent
from app.agents.test_writer import TestWriterAgent
from app.agents.test_executor import TestExecutorAgent
from app.agents.coverage import CoverageAgent
from app.agents.ci_agent import CIAgent
from app.agents.llm_test_generator import LLMTestGenerator


class TestGenerationOrchestrator:
    """
    Main orchestration layer for:
    - repository analysis
    - function extraction
    - edge case detection
    - AI test generation
    - pytest execution
    - coverage reporting
    """

    MAX_FILES_TO_ANALYZE = 15
    MAX_FUNCTIONS_TO_ANALYZE = 10
    MAX_FILE_SIZE = 50000

    def __init__(self):

        self.job_id = str(uuid.uuid4())

        self.repo_scanner = RepoScannerAgent("")
        self.code_understanding = CodeUnderstandingAgent("")
        self.edge_case_finder = EdgeCaseFinderAgent()
        self.test_writer = TestWriterAgent()
        self.test_executor = TestExecutorAgent()
        self.coverage_agent = CoverageAgent()
        self.ci_agent = CIAgent()

        self.llm_test_generator = LLMTestGenerator()

        self.generated_tests_dir = os.path.abspath(
            "generated_tests"
        )

        os.makedirs(
            self.generated_tests_dir,
            exist_ok=True
        )

    # ==========================================================
    # CLEANUP GENERATED FILES
    # ==========================================================

    def _cleanup_generated_tests(self):

        if not os.path.exists(
            self.generated_tests_dir
        ):
            return

        for file_name in os.listdir(
            self.generated_tests_dir
        ):

            if (
                file_name.startswith("test_")
                or file_name.startswith("temp_code")
            ):

                try:

                    os.remove(
                        os.path.join(
                            self.generated_tests_dir,
                            file_name
                        )
                    )

                except Exception:
                    pass

    # ==========================================================
    # SAVE TEMP SOURCE
    # ==========================================================

    def _save_temp_source_code(
        self,
        source_code: str,
        language: str = "python"
    ) -> str:

        extension = (
            "py"
            if language == "python"
            else "js"
        )

        temp_source_path = os.path.join(
            self.generated_tests_dir,
            f"temp_code.{extension}"
        )

        with open(
            temp_source_path,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(source_code)

        return temp_source_path

    # ==========================================================
    # PYTHON EXTRACTION
    # ==========================================================

    def _extract_python_functions(
        self,
        source_code: str,
        file_name: str
    ) -> List[Dict[str, Any]]:

        functions = []

        try:

            tree = ast.parse(source_code)

            source_lines = source_code.splitlines()

            for node in ast.walk(tree):

                if not isinstance(
                    node,
                    (
                        ast.FunctionDef,
                        ast.AsyncFunctionDef
                    )
                ):
                    continue

                start_line = node.lineno

                end_line = getattr(
                    node,
                    "end_lineno",
                    start_line + 20
                )

                function_source = "\n".join(
                    source_lines[
                        start_line - 1:end_line
                    ]
                )

                args = []

                for arg in node.args.args:

                    args.append({
                        "name": arg.arg
                    })

                functions.append({
                    "name": node.name,
                    "file": file_name,
                    "language": "python",
                    "signature": f"def {node.name}",
                    "args": args,
                    "context": function_source,
                    "full_source": function_source,
                    "lineno": start_line
                })

        except Exception as e:

            print(
                f"[PYTHON EXTRACTION ERROR] {e}"
            )

        return functions

    # ==========================================================
    # JS EXTRACTION
    # ==========================================================

    def _extract_js_functions(
        self,
        source_code: str,
        file_name: str
    ) -> List[Dict[str, Any]]:

        functions = []

        patterns = [

            r'function\s+(\w+)\s*\((.*?)\)',

            r'const\s+(\w+)\s*=\s*\((.*?)\)\s*=>',

            r'export\s+function\s+(\w+)\s*\((.*?)\)'
        ]

        try:

            for pattern in patterns:

                for match in re.finditer(
                    pattern,
                    source_code
                ):

                    func_name = match.group(1)

                    raw_args = match.group(2)

                    args = []

                    for arg in raw_args.split(","):

                        arg = arg.strip()

                        if arg:

                            args.append({
                                "name": arg
                            })

                    start_pos = max(
                        0,
                        match.start() - 200
                    )

                    end_pos = min(
                        len(source_code),
                        match.end() + 800
                    )

                    function_source = source_code[
                        start_pos:end_pos
                    ]

                    functions.append({
                        "name": func_name,
                        "file": file_name,
                        "language": "javascript",
                        "signature": match.group(0),
                        "args": args,
                        "context": function_source,
                        "full_source": function_source
                    })

        except Exception as e:

            print(
                f"[JS EXTRACTION ERROR] {e}"
            )

        return functions

    # ==========================================================
    # FUNCTION ROUTER
    # ==========================================================

    def _extract_functions(
        self,
        source_code: str,
        language: str,
        file_name: str
    ) -> List[Dict[str, Any]]:

        if language == "python":

            return self._extract_python_functions(
                source_code,
                file_name
            )

        return self._extract_js_functions(
            source_code,
            file_name
        )

    # ==========================================================
    # FUNCTION INFO
    # ==========================================================

    def _build_function_info(
        self,
        func: Dict[str, Any]
    ) -> Dict[str, Any]:

        return {
            "name": func["name"],
            "docstring": func.get(
                "context",
                ""
            ),
            "args": func.get(
                "args",
                []
            ),
            "source_code": func.get(
                "context",
                ""
            )
        }

    # ==========================================================
    # MODULE IMPORT
    # ==========================================================

    def _build_module_import(
        self,
        file_path: str
    ) -> str:

        module_path = (
            file_path
            .replace("/", ".")
            .replace("\\", ".")
        )

        module_path = re.sub(
            r"\.(py|js|ts)$",
            "",
            module_path
        )

        return module_path

    # ==========================================================
    # FIX IMPORTS
    # ==========================================================

    def _fix_test_imports(
        self,
        test_content: str,
        module_name: str,
        function_name: str = None
    ) -> str:

        # Start with sys.path at the VERY TOP (first thing!)
        fixed_content = (
            "import sys, os\n"
            "sys.path.insert(0, os.path.dirname(__file__))\n\n"
        )

        # Then add pytest import
        fixed_content += "import pytest\n"

        # Then add function import if needed
        if function_name:
            fixed_content += (
                f"from {module_name} "
                f"import {function_name}\n"
            )

        # Then add the actual test content (without duplicating imports)
        test_lines = test_content.strip().split("\n")
        filtered_lines = []

        for line in test_lines:

            stripped = line.strip()

            # Skip import lines we've already added
            if (
                stripped.startswith("import pytest")
                or stripped.startswith("from temp_code import")
                or stripped.startswith("from " + module_name)
                or stripped.startswith("import sys")
                or stripped.startswith("import os")
                or stripped.startswith("sys.path")
                or not stripped
            ):
                continue

            filtered_lines.append(line)

        fixed_content += "\n".join(filtered_lines)

        # Replace placeholder imports
        replacements = [
            (
                "from your_module import",
                f"from {module_name} import"
            ),
            (
                "from module import",
                f"from {module_name} import"
            ),
            (
                "import your_module",
                f"import {module_name}"
            )
        ]

        for old, new in replacements:

            fixed_content = fixed_content.replace(
                old,
                new
            )

        return fixed_content.strip()

    # ==========================================================
    # VALIDATE PYTHON TEST
    # ==========================================================

    def _validate_python_test(
        self,
        code: str
    ) -> bool:

        try:

            ast.parse(code)

            if "test_" not in code:
                return False

            return True

        except Exception as e:

            print(
                f"[TEST VALIDATION ERROR] {e}"
            )

            return False

    # ==========================================================
    # SAVE TESTS
    # ==========================================================

    def _save_generated_tests(
        self,
        tests: List[Dict[str, Any]]
    ) -> List[str]:

        saved_files = []

        for index, test in enumerate(tests):

            try:

                target = test.get(
                    "target_function",
                    f"generated_{index}"
                )

                language = test.get(
                    "language",
                    "python"
                )

                extension = (
                    "py"
                    if language == "python"
                    else "js"
                )

                file_name = (
                    f"test_{target}_{index}.{extension}"
                )

                file_path = os.path.join(
                    self.generated_tests_dir,
                    file_name
                )

                with open(
                    file_path,
                    "w",
                    encoding="utf-8"
                ) as f:

                    f.write(
                        test["content"]
                    )

                saved_files.append(
                    file_path
                )

            except Exception as e:

                print(
                    f"[SAVE TEST ERROR] {e}"
                )

        return saved_files

    # ==========================================================
    # RUN PYTEST
    # ==========================================================

    def _run_pytest(
        self,
        test_files: List[str]
    ) -> List[Dict[str, Any]]:

        results = []

        for test_file in test_files:

            start_time = time.time()

            try:

                env = os.environ.copy()

                env["PYTHONPATH"] = (
                    os.getcwd()
                    + os.pathsep
                    + self.generated_tests_dir
                )

                process = subprocess.run(
                    [
                        "python",
                        "-m",
                        "pytest",
                        test_file,
                        "-v",
                        "--tb=short"
                    ],
                    cwd=os.getcwd(),
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                duration = round(
                    time.time() - start_time,
                    2
                )

                results.append({
                    "file": test_file,
                    "status": (
                        "passed"
                        if process.returncode == 0
                        else "failed"
                    ),
                    "duration": duration,
                    "output": process.stdout,
                    "errors": process.stderr
                })

            except subprocess.TimeoutExpired:

                results.append({
                    "file": test_file,
                    "status": "timeout",
                    "duration": 60,
                    "output": "",
                    "errors": "Pytest timed out"
                })

            except Exception as e:

                results.append({
                    "file": test_file,
                    "status": "error",
                    "duration": 0,
                    "output": "",
                    "errors": str(e)
                })

        return results

    # ==========================================================
    # ANALYZE REPOSITORY
    # ==========================================================

    def analyze_repository(
        self,
        repo_path: str
    ) -> Dict[str, Any]:

        print(
            f"[Job {self.job_id}] Starting analysis"
        )

        self._cleanup_generated_tests()

        self.repo_scanner = RepoScannerAgent(
            repo_path
        )

        repo_structure = (
            self.repo_scanner.scan()
        )

        files_to_analyze = [

            file_path

            for file_path in repo_structure.get(
                "files",
                []
            )

            if file_path.endswith(
                (
                    ".py",
                    ".js",
                    ".ts"
                )
            )

        ][:self.MAX_FILES_TO_ANALYZE]

        functions_data = []

        for file_path in files_to_analyze:

            full_path = os.path.join(
                repo_path,
                file_path
            )

            try:

                with open(
                    full_path,
                    "r",
                    encoding="utf-8",
                    errors="ignore"
                ) as f:

                    content = f.read()

                if (
                    len(content)
                    > self.MAX_FILE_SIZE
                ):
                    continue

                language = (
                    "python"
                    if file_path.endswith(".py")
                    else "javascript"
                )

                extracted = self._extract_functions(
                    content,
                    language,
                    file_path
                )

                functions_data.extend(
                    extracted
                )

            except Exception as e:

                print(
                    f"[FILE READ ERROR] "
                    f"{file_path}: {e}"
                )

        functions_data = functions_data[
            :self.MAX_FUNCTIONS_TO_ANALYZE
        ]

        edge_cases_list = []

        for func in functions_data:

            try:

                func_info = (
                    self._build_function_info(
                        func
                    )
                )

                print(
                    f"[EDGE CASE] Processing "
                    f"{func['name']} with "
                    f"args: {func_info.get('args', [])}"
                )

                edge_cases = (
                    self.edge_case_finder.find_edge_cases(
                        func_info,
                        ""
                    )
                )

                print(
                    f"[EDGE CASE] Found "
                    f"{len(edge_cases)} cases for "
                    f"{func['name']}"
                )

                edge_cases_list.extend(
                    edge_cases[:10]
                )

            except Exception as e:

                import traceback

                print(
                    f"[EDGE CASE ERROR] {e}"
                )

                print(traceback.format_exc())

        generated_tests = []

        for func in functions_data:

            try:

                module_name = (
                    self._build_module_import(
                        func["file"]
                    )
                )

                print(
                    f"[TEST GEN] Generating for "
                    f"function: {func['name']}"
                )

                llm_tests = (
                    self.llm_test_generator.generate_tests_from_code(
                        func["context"],
                        func["name"],
                        func["language"]
                    )
                )

                print(
                    f"[TEST GEN] LLM returned "
                    f"{len(llm_tests)} test(s)"
                )

                valid_tests = []

                for test in llm_tests:

                    content = test.get(
                        "content",
                        ""
                    )

                    print(
                        f"[TEST GEN] Test content "
                        f"length: {len(content)}"
                    )

                    if not content:

                        print(
                            f"[TEST GEN] Empty content!"
                        )
                        continue

                    content = (
                        self._fix_test_imports(
                            content,
                            module_name,
                            func["name"]
                        )
                    )

                    test["content"] = content

                    test["target_function"] = (
                        func["name"]
                    )

                    if (
                        func["language"]
                        == "python"
                    ):

                        if self._validate_python_test(
                            content
                        ):

                            print(
                                f"[TEST GEN] Test "
                                f"validated OK"
                            )

                            valid_tests.append(
                                test
                            )

                        else:

                            print(
                                f"[TEST GEN] Test "
                                f"validation failed"
                            )

                    else:

                        valid_tests.append(
                            test
                        )

                print(
                    f"[TEST GEN] Valid tests: "
                    f"{len(valid_tests)}"
                )

                generated_tests.extend(
                    valid_tests
                )

                print(
                    f"[TEST GEN] Total in "
                    f"generated_tests: "
                    f"{len(generated_tests)}"
                )

            except Exception as e:

                import traceback

                print(
                    f"[TEST GENERATION ERROR] {e}"
                )

                print(traceback.format_exc())

        print(
            f"[ORCHESTRATOR] Before save: "
            f"{len(generated_tests)} tests"
        )

        saved_test_files = (
            self._save_generated_tests(
                generated_tests
            )
        )

        test_results = self._run_pytest(
            saved_test_files
        )

        try:

            coverage_report = (
                self.coverage_agent.compute_coverage(
                    test_results,
                    files_to_analyze,
                    "python"
                )
            )

        except Exception as e:

            coverage_report = {
                "status": "error",
                "message": str(e)
            }

        print(
            f"[ORCHESTRATOR] Returning "
            f"{len(generated_tests)} tests"
        )

        return {

            "job_id": self.job_id,

            "status": "COMPLETED",

            "structure": {

                "languages": repo_structure.get(
                    "languages",
                    {}
                ),

                "files": files_to_analyze,

                "functions": [
                    {
                        "name": f["name"],
                        "file": f["file"]
                    }
                    for f in functions_data
                ]
            },

            "edge_cases": edge_cases_list[:20],

            "tests": generated_tests,

            "saved_test_files": saved_test_files,

            "test_results": test_results,

            "coverage": coverage_report,

            "suggestions": [
                "AI tests generated successfully",
                "Edge cases analyzed",
                "Tests executed with pytest"
            ],

            "llm_provider": "groq",

            "api_calls_made": len(
                generated_tests
            )
        }

    # ==========================================================
    # ANALYZE GITHUB URL
    # ==========================================================

    def analyze_from_url(
        self,
        github_url: str
    ):

        repo_path = tempfile.mkdtemp()

        RepoScannerAgent.clone_from_github(
            github_url,
            repo_path
        )

        return self.analyze_repository(
            repo_path
        )

    # ==========================================================
    # ANALYZE ZIP
    # ==========================================================

    def analyze_from_zip(
        self,
        zip_path: str
    ):

        extract_to = tempfile.mkdtemp()

        RepoScannerAgent.extract_from_zip(
            zip_path,
            extract_to
        )

        for item in os.listdir(extract_to):

            item_path = os.path.join(
                extract_to,
                item
            )

            if os.path.isdir(item_path):

                return self.analyze_repository(
                    item_path
                )

        return self.analyze_repository(
            extract_to
        )

    # ==========================================================
    # ANALYZE RAW CODE
    # ==========================================================

    def analyze_from_text(
        self,
        source_code: str,
        language: str = "python"
    ):

        temp_dir = tempfile.mkdtemp()

        extension = (
            "py"
            if language == "python"
            else "js"
        )

        file_path = os.path.join(
            temp_dir,
            f"temp_code.{extension}"
        )

        with open(
            file_path,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(source_code)

        self._save_temp_source_code(
            source_code,
            language
        )

        return self.analyze_repository(
            temp_dir
        )