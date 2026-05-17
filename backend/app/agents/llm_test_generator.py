"""
LLM-based test generator using Groq API
for AI-generated comprehensive tests.
"""

import ast
import json
import re
import time

from typing import Dict, List, Any

from groq import Groq
from groq import RateLimitError

from app.core.config import settings


class LLMTestGenerator:
    """
    Generates tests using Groq LLM.
    """

    def __init__(self):

        self.api_key = settings.groq_api_key

        self.model = settings.groq_model

        self.has_valid_key = bool(
            self.api_key and
            self.api_key.strip() and
            self.api_key != "your-groq-api-key-here"
        )

        self.client = None

        if self.has_valid_key:

            self.client = Groq(
                api_key=self.api_key
            )

        print(
            f"[LLM] Initialized | "
            f"model={self.model} | "
            f"has_valid_key={self.has_valid_key}"
        )

    # ==========================================================
    # MAIN TEST GENERATION
    # ==========================================================

    def generate_tests_from_code(
        self,
        function_code: str,
        function_name: str,
        language: str = "python"
    ) -> List[Dict[str, Any]]:

        try:

            if not self.has_valid_key:

                return self._generate_demo_tests(
                    function_name,
                    language,
                    "comprehensive"
                )

            prompt = self._create_test_generation_prompt(
                function_code,
                function_name,
                language
            )

            print(
                f"[LLM] Generating tests for "
                f"{function_name}"
            )

            response = self._call_llm(prompt)

            # Detect and handle truncation
            if self._detect_truncation(response):
                print(
                    f"[LLM] Detected truncated output. "
                    f"Requesting continuation..."
                )
                response = self._get_continuation(
                    response
                )
                print(
                    f"[LLM] Complete test code generated"
                )

            cleaned = self._clean_code_response(
                response
            )

            cleaned = self._remove_duplicate_tests(
                cleaned
            )

            cleaned = self._normalize_imports(
                cleaned
            )

            if language == "python":

                cleaned = self._repair_python_code(
                    cleaned
                )

                if not self._is_valid_python(
                    cleaned
                ):

                    raise ValueError(
                        "Generated invalid Python"
                    )

            return [{
                "id": (
                    f"llm_test_"
                    f"{function_name}"
                ),

                "test_type": "comprehensive",

                "target_function": function_name,

                "language": language,

                "content": cleaned,

                "file_path": (
                    f"test_{function_name}.py"
                    if language == "python"
                    else f"test_{function_name}.js"
                ),

                "generated_by": "groq"
            }]

        except Exception as e:

            import traceback

            print(
                f"[LLM] Generation failed: "
                f"{type(e).__name__}: {e}"
            )

            print(traceback.format_exc())

            return self._generate_demo_tests(
                function_name,
                language,
                "fallback"
            )

    # ==========================================================
    # LLM CALL
    # ==========================================================

    def _call_llm(
        self,
        prompt: str,
        continuation: bool = False
    ) -> str:

        completion = None

        for attempt in range(5):

            try:

                completion = (
                    self.client.chat.completions.create(
                        model=self.model,

                        temperature=0.1,

                        max_tokens=3500,

                        messages=[
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ]
                    )
                )

                break

            except RateLimitError:

                wait_time = 5 * (attempt + 1)

                print(
                    f"[LLM] Rate limited. "
                    f"Retrying in {wait_time}s"
                )

                time.sleep(wait_time)

        if completion is None:

            raise RuntimeError(
                "Groq request failed"
            )

        content = (
            completion
            .choices[0]
            .message.content
        )

        if not content:

            raise ValueError(
                "Empty response from LLM"
            )

        return content

    # ==========================================================
    # DETECT TRUNCATION
    # ==========================================================

    def _detect_truncation(
        self,
        chunk: str
    ) -> bool:

        """Detect if LLM response is truncated (incomplete)"""

        if not chunk:
            return False

        is_truncated = False

        # Check 1: Ends mid-word (incomplete identifier)
        stripped = chunk.strip()
        if stripped and stripped[-1].isalnum() and not stripped.endswith(")"):
            is_truncated = True

        # Check 2: Incomplete function definition
        if (stripped.endswith("def ") or (
            "def test_" in stripped[-50:] and "(" not in stripped[-30:]
        )):
            is_truncated = True

        # Check 3: Incomplete assert or with statement
        if (stripped.endswith(("assert ", "with ", "raise ")) or (
            "pytest.raises" in stripped[-60:] and ")" not in stripped[-20:]
        )):
            is_truncated = True

        # Check 4: Large chunk (likely truncated)
        if len(chunk) > 3000:
            is_truncated = True

        return is_truncated

    # ==========================================================
    # GET CONTINUED LLM RESPONSE
    # ==========================================================

    def _get_continuation(
        self,
        original_response: str
    ) -> str:

        """Get continuation of truncated response"""

        prompt = (
            "Continue generating the remaining pytest code. "
            "Do not repeat previous code. "
            "Generate complete, valid Python test code:\n\n"
            f"Previous code:\n{original_response}"
        )

        try:
            continuation = self._call_llm(
                prompt,
                continuation=True
            )
            return original_response + "\n" + continuation
        except Exception as e:
            print(f"[LLM] Continuation failed: {e}")
            return original_response

    # ==========================================================
    # CLEAN RESPONSE
    # ==========================================================

    def _clean_code_response(
        self,
        text: str
    ) -> str:

        if not text:

            return ""

        replacements = [
            "```python",
            "```javascript",
            "```json",
            "```pytest",
            "```"
        ]

        for item in replacements:

            text = text.replace(
                item,
                ""
            )

        text = text.strip()

        return text

    # ==========================================================
    # REMOVE DUPLICATE TESTS
    # ==========================================================

    def _remove_duplicate_tests(
        self,
        code: str
    ) -> str:

        lines = code.splitlines()

        seen_tests = set()

        cleaned = []

        current_block = []

        current_name = None

        for line in lines:

            if line.startswith("def test_"):

                if current_name:

                    if current_name not in seen_tests:

                        seen_tests.add(
                            current_name
                        )

                        cleaned.extend(
                            current_block
                        )

                current_block = [line]

                current_name = line.strip()

            else:

                current_block.append(line)

        if current_name:

            if current_name not in seen_tests:

                cleaned.extend(current_block)

        return "\n".join(cleaned)

    # ==========================================================
    # NORMALIZE IMPORTS
    # ==========================================================

    def _normalize_imports(
        self,
        code: str
    ) -> str:

        imports = []

        body = []

        for line in code.splitlines():

            stripped = line.strip()

            if (
                stripped.startswith("import ")
                or stripped.startswith("from ")
            ):

                if stripped not in imports:

                    imports.append(stripped)

            else:

                body.append(line)

        final_code = (
            "\n".join(imports)
            + "\n\n"
            + "\n".join(body)
        )

        return final_code.strip()

    # ==========================================================
    # VALIDATE PYTHON
    # ==========================================================

    def _is_valid_python(
        self,
        code: str
    ) -> bool:

        try:

            ast.parse(code)

            return True

        except Exception:

            return False

    # ==========================================================
    # CHECK COMPLETE TEST CODE
    # ==========================================================

    def _is_complete_test_code(
        self,
        code: str,
        language: str
    ) -> bool:

        if not code:

            return False

        stripped = code.strip()

        bad_endings = [

            "(",
            "[",
            "{",
            ",",
            ":",
            "\\",

            "assert",

            "with pytest.raises",

            "result =",

            "with pytest.raises(TypeError)",

            "with pytest.raises(ValueError)"
        ]

        for ending in bad_endings:

            if stripped.endswith(ending):

                return False

        if language == "python":

            return self._is_valid_python(
                code
            )

        return True

    # ==========================================================
    # REPAIR TRUNCATED PYTHON
    # ==========================================================

    def _repair_truncated_python(
        self,
        code: str
    ) -> str:

        lines = code.splitlines()

        repaired = []

        for line in lines:

            repaired.append(line)

        if repaired:

            last = repaired[-1].strip()

            if (
                "with pytest.raises" in last
                and not last.endswith(":")
            ):

                repaired[-1] += ":"

                repaired.append(
                    "        pass"
                )

            elif last.endswith(":"):

                repaired.append(
                    "        pass"
                )

        return "\n".join(repaired)

    # ==========================================================
    # REPAIR PYTHON
    # ==========================================================

    def _repair_python_code(
        self,
        code: str
    ) -> str:

        code = code.strip()

        if not code.endswith("\n"):

            code += "\n"

        return code

    # ==========================================================
    # DEMO TESTS
    # ==========================================================

    def _generate_demo_tests(
        self,
        function_name: str,
        language: str,
        test_type: str
    ) -> List[Dict[str, Any]]:

        if language == "python":

            test_code = f"""
import pytest

def test_{function_name}_basic():
    assert True
"""

        else:

            test_code = f"""
describe("{function_name}", () => {{
    test("basic", () => {{
        expect(true).toBe(true);
    }});
}});
"""

        return [{
            "id": (
                f"demo_test_"
                f"{function_name}"
            ),

            "test_type": test_type,

            "target_function": function_name,

            "language": language,

            "content": test_code.strip(),

            "generated_by": "demo"
        }]

    # ==========================================================
    # TEST GENERATION PROMPT
    # ==========================================================

    def _create_test_generation_prompt(
        self,
        function_code: str,
        function_name: str,
        language: str
    ) -> str:

        if language == "python":

            return f"""
You are an expert Python test engineer.

Generate clean executable pytest tests.

STRICT RULES:
- ONLY return executable Python code
- NO markdown
- NO explanations
- NO duplicate tests
- Keep total tests under 12
- Generate concise tests only
- IMPORT EXACTLY:
from temp_code import {function_name}

Generate:
1. Happy path tests
2. Edge cases
3. Invalid input tests
4. Boundary tests
5. pytest.raises tests

Function Name:
{function_name}

Function Code:
{function_code}
"""

        return f"""
You are an expert JavaScript Jest engineer.

Generate executable Jest tests.

STRICT RULES:
- ONLY return executable code
- NO markdown
- NO explanations
- NO duplicate tests
- Keep tests concise

Function:
{function_name}

Code:
{function_code}
"""

    # ==========================================================
    # EDGE CASE PROMPT
    # ==========================================================

    def _create_edge_case_prompt(
        self,
        function_code: str,
        function_name: str,
        edge_cases: List[Dict[str, Any]],
        language: str
    ) -> str:

        edge_cases_text = json.dumps(
            edge_cases,
            indent=2
        )

        return f"""
Generate concise executable pytest edge-case tests.

IMPORT:
from temp_code import {function_name}

Edge Cases:
{edge_cases_text}

Function:
{function_code}

ONLY RETURN CODE.
"""