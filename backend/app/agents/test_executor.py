import os
import time
import shutil
import tempfile
import subprocess

from typing import Dict, List, Any

try:

    import docker

except ImportError:

    docker = None


class TestExecutorAgent:
    """
    Executes generated tests safely.

    Features:
    - Pytest execution
    - Jest execution
    - Timeout protection
    - Docker isolation
    - Proper stdout/stderr handling
    - Import-safe execution
    """

    def __init__(
        self,
        docker_image: str = "python:3.11-slim"
    ):

        self.docker_image = docker_image

        self.client = None

        if docker:

            try:

                self.client = docker.from_env()

            except Exception as e:

                print(
                    f"[TestExecutor] "
                    f"Docker unavailable: {e}"
                )

    # ==========================================================
    # EXECUTE MULTIPLE TESTS
    # ==========================================================

    def execute_tests(
        self,
        tests: List[Dict[str, Any]],
        language: str
    ) -> List[Dict[str, Any]]:

        results = []

        for test in tests:

            result = self._execute_single_test(
                test,
                language
            )

            results.append(result)

        return results

    # ==========================================================
    # EXECUTE SINGLE TEST
    # ==========================================================

    def _execute_single_test(
        self,
        test: Dict[str, Any],
        language: str
    ) -> Dict[str, Any]:

        test_content = test.get(
            "content",
            ""
        )

        test_type = test.get(
            "test_type",
            test.get("type", "unit")
        )

        if language == "python":

            return self._execute_python_test(
                test_content,
                test_type
            )

        elif language == "javascript":

            return self._execute_js_test(
                test_content,
                test_type
            )

        return {
            "status": "ERROR",
            "output": "",
            "error": (
                f"Unsupported language: "
                f"{language}"
            ),
            "duration": 0,
            "test_type": test_type
        }

    # ==========================================================
    # EXECUTE PYTHON TEST
    # ==========================================================

    def _execute_python_test(
        self,
        test_content: str,
        test_type: str
    ) -> Dict[str, Any]:

        start_time = time.time()

        temp_dir = None

        try:

            # --------------------------------------------------
            # VALIDATE PYTEST
            # --------------------------------------------------

            if shutil.which("pytest") is None:

                return {
                    "status": "ERROR",
                    "output": "",
                    "error": (
                        "pytest not installed"
                    ),
                    "duration": 0,
                    "test_type": test_type
                }

            # --------------------------------------------------
            # TEMP EXECUTION ENV
            # --------------------------------------------------

            temp_dir = tempfile.mkdtemp()

            test_file = os.path.join(
                temp_dir,
                "test_generated.py"
            )

            # --------------------------------------------------
            # COPY temp_code.py
            # --------------------------------------------------

            generated_temp_code = os.path.join(
                os.getcwd(),
                "generated_tests",
                "temp_code.py"
            )

            if os.path.exists(
                generated_temp_code
            ):

                shutil.copy(
                    generated_temp_code,
                    os.path.join(
                        temp_dir,
                        "temp_code.py"
                    )
                )

            # --------------------------------------------------
            # WRITE TEST FILE
            # --------------------------------------------------

            with open(
                test_file,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(test_content)

            # --------------------------------------------------
            # ENVIRONMENT
            # --------------------------------------------------

            env = os.environ.copy()

            existing_pythonpath = env.get(
                "PYTHONPATH",
                ""
            )

            env["PYTHONPATH"] = (
                temp_dir
                + os.pathsep
                + os.getcwd()
                + os.pathsep
                + existing_pythonpath
            )

            # --------------------------------------------------
            # RUN PYTEST
            # --------------------------------------------------

            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "pytest",
                    test_file,
                    "-v",
                    "--tb=short",
                    "--disable-warnings"
                ],
                cwd=temp_dir,
                env=env,
                capture_output=True,
                text=True,
                timeout=45
            )

            duration = round(
                time.time() - start_time,
                2
            )

            status = (
                "PASSED"
                if result.returncode == 0
                else "FAILED"
            )

            combined_output = (
                result.stdout
                + "\n"
                + result.stderr
            )

            return {
                "status": status,
                "output": combined_output.strip(),
                "error": (
                    None
                    if result.returncode == 0
                    else result.stderr.strip()
                ),
                "duration": duration,
                "test_type": test_type
            }

        except subprocess.TimeoutExpired:

            return {
                "status": "TIMEOUT",
                "output": "",
                "error": (
                    "Test execution timed out"
                ),
                "duration": 45,
                "test_type": test_type
            }

        except Exception as e:

            return {
                "status": "ERROR",
                "output": "",
                "error": str(e),
                "duration": 0,
                "test_type": test_type
            }

        finally:

            if (
                temp_dir and
                os.path.exists(temp_dir)
            ):

                shutil.rmtree(
                    temp_dir,
                    ignore_errors=True
                )

    # ==========================================================
    # EXECUTE JS TEST
    # ==========================================================

    def _execute_js_test(
        self,
        test_content: str,
        test_type: str
    ) -> Dict[str, Any]:

        start_time = time.time()

        temp_dir = None

        try:

            if shutil.which("npx") is None:

                return {
                    "status": "ERROR",
                    "output": "",
                    "error": "Node.js/npm not installed",
                    "duration": 0,
                    "test_type": test_type
                }

            temp_dir = tempfile.mkdtemp()

            test_file = os.path.join(
                temp_dir,
                "generated.test.js"
            )

            with open(
                test_file,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(test_content)

            result = subprocess.run(
                [
                    "npx",
                    "jest",
                    test_file,
                    "--runInBand"
                ],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=45
            )

            duration = round(
                time.time() - start_time,
                2
            )

            status = (
                "PASSED"
                if result.returncode == 0
                else "FAILED"
            )

            combined_output = (
                result.stdout
                + "\n"
                + result.stderr
            )

            return {
                "status": status,
                "output": combined_output.strip(),
                "error": (
                    None
                    if result.returncode == 0
                    else result.stderr.strip()
                ),
                "duration": duration,
                "test_type": test_type
            }

        except subprocess.TimeoutExpired:

            return {
                "status": "TIMEOUT",
                "output": "",
                "error": (
                    "Jest execution timed out"
                ),
                "duration": 45,
                "test_type": test_type
            }

        except Exception as e:

            return {
                "status": "ERROR",
                "output": "",
                "error": str(e),
                "duration": 0,
                "test_type": test_type
            }

        finally:

            if (
                temp_dir and
                os.path.exists(temp_dir)
            ):

                shutil.rmtree(
                    temp_dir,
                    ignore_errors=True
                )

    # ==========================================================
    # EXECUTE INSIDE DOCKER
    # ==========================================================

    def execute_in_docker(
        self,
        test_content: str,
        language: str
    ) -> Dict[str, Any]:

        if not self.client:

            return {
                "status": "ERROR",
                "output": "",
                "error": "Docker unavailable",
                "duration": 0
            }

        start_time = time.time()

        temp_dir = None

        try:

            temp_dir = tempfile.mkdtemp()

            extension = (
                "py"
                if language == "python"
                else "js"
            )

            script_name = (
                f"test_generated.{extension}"
            )

            script_path = os.path.join(
                temp_dir,
                script_name
            )

            with open(
                script_path,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(test_content)

            if language == "python":

                command = (
                    f"pytest {script_name} -v"
                )

            else:

                command = (
                    f"npx jest {script_name}"
                )

            output = self.client.containers.run(
                self.docker_image,
                command,
                working_dir="/workspace",
                volumes={
                    temp_dir: {
                        "bind": "/workspace",
                        "mode": "rw"
                    }
                },
                remove=True,
                stderr=True,
                stdout=True
            )

            duration = round(
                time.time() - start_time,
                2
            )

            return {
                "status": "COMPLETED",
                "output": output.decode(
                    "utf-8",
                    errors="ignore"
                ),
                "error": None,
                "duration": duration
            }

        except Exception as e:

            return {
                "status": "ERROR",
                "output": "",
                "error": str(e),
                "duration": 0
            }

        finally:

            if (
                temp_dir and
                os.path.exists(temp_dir)
            ):

                shutil.rmtree(
                    temp_dir,
                    ignore_errors=True
                )