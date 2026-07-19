"""Groq-backed pytest generator.

Functions are batched into a single request where possible to minimise API
calls (and rate-limit pressure). Failed requests use exponential backoff with
jitter. Without a valid API key the generator returns deterministic "demo"
tests so the pipeline still works offline.
"""

import ast
import logging
import random
import re
import time
from typing import Any, Dict, List

from app.core.config import settings

logger = logging.getLogger(__name__)

_MAX_TOKENS = 2048
_MAX_RETRIES = 4
_MARKER = "### FUNCTION:"


class LLMTestGenerator:
    def __init__(self) -> None:
        self.model = settings.groq_model
        self.has_valid_key = settings.has_groq_key
        self._client = None
        if self.has_valid_key:
            from groq import Groq

            self._client = Groq(api_key=settings.groq_api_key)
        logger.info("LLM ready (model=%s, live=%s)", self.model, self.has_valid_key)

    # ------------------------------------------------------------------
    def generate_tests(self, functions: List[Dict[str, Any]]) -> Dict[str, str]:
        """Return {function_name: pytest_code} for every function.

        Batches up to ``LLM_BATCH_SIZE`` functions per request.
        """
        results: Dict[str, str] = {}
        if not functions:
            return results
        if not self.has_valid_key:
            return {fn["name"]: self._demo_test(fn["name"]) for fn in functions}

        batch_size = max(1, settings.llm_batch_size)
        for start in range(0, len(functions), batch_size):
            batch = functions[start : start + batch_size]
            parsed: Dict[str, str] = {}
            try:
                raw = self._call_llm(self._batch_prompt(batch))
                parsed = self._parse_batch(raw, [fn["name"] for fn in batch])
            except Exception as exc:  # noqa: BLE001 - degrade to demo tests
                logger.warning("Batch generation failed: %s", exc)

            for fn in batch:
                code = self._clean(parsed.get(fn["name"], ""))
                results[fn["name"]] = code if self._is_valid_python(code) else self._demo_test(fn["name"])
        return results

    # ------------------------------------------------------------------
    def _call_llm(self, prompt: str) -> str:
        from groq import RateLimitError

        for attempt in range(_MAX_RETRIES):
            try:
                completion = self._client.chat.completions.create(
                    model=self.model,
                    temperature=0.1,
                    max_tokens=_MAX_TOKENS,
                    messages=[{"role": "user", "content": prompt}],
                )
                content = completion.choices[0].message.content
                if not content:
                    raise ValueError("Empty response from LLM")
                return content
            except RateLimitError:
                if attempt == _MAX_RETRIES - 1:
                    raise
                wait = min(2 ** attempt + random.uniform(0, 1), 20)
                logger.info("Rate limited; backing off %.1fs", wait)
                time.sleep(wait)
        raise RuntimeError("Groq request failed after retries")

    @staticmethod
    def _batch_prompt(functions: List[Dict[str, Any]]) -> str:
        blocks = []
        for fn in functions:
            blocks.append(f"{_MARKER} {fn['name']}\n{fn['context']}")
        joined = "\n\n".join(blocks)
        return f"""You are an expert Python test engineer. Write concise, correct pytest tests.

Rules:
- Output ONLY Python code (no markdown fences, no prose).
- For EACH function below, emit a line `{_MARKER} <name>` then its tests.
- Import each function exactly as `from temp_code import <name>`.
- Cover happy paths, edge cases, invalid inputs, boundaries, and expected
  exceptions via `pytest.raises`. Max ~8 tests per function.
- Do not redefine the function under test.

Functions:

{joined}
"""

    @classmethod
    def _parse_batch(cls, raw: str, names: List[str]) -> Dict[str, str]:
        """Split a batched response into {name: code} using the marker lines."""
        text = cls._strip_fences(raw)
        pattern = re.compile(rf"^{re.escape(_MARKER)}\s*(\w+)\s*$", re.MULTILINE)
        matches = list(pattern.finditer(text))
        sections: Dict[str, str] = {}
        for i, match in enumerate(matches):
            name = match.group(1)
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            sections[name] = text[match.end() : end].strip()
        # If the model ignored markers and there's a single function, take it all.
        if not sections and len(names) == 1:
            sections[names[0]] = text.strip()
        return sections

    @staticmethod
    def _strip_fences(text: str) -> str:
        for fence in ("```python", "```pytest", "```json", "```"):
            text = text.replace(fence, "")
        return text

    @classmethod
    def _clean(cls, text: str) -> str:
        if not text:
            return ""
        text = cls._strip_fences(text)
        seen, imports, body = set(), [], []
        for line in text.strip().splitlines():
            stripped = line.strip()
            if stripped.startswith(("import ", "from ")):
                if stripped not in seen:
                    seen.add(stripped)
                    imports.append(stripped)
            else:
                body.append(line)
        return ("\n".join(imports) + "\n\n" + "\n".join(body)).strip()

    @staticmethod
    def _is_valid_python(code: str) -> bool:
        if not code or "test_" not in code:
            return False
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False

    @staticmethod
    def _demo_test(function_name: str) -> str:
        return (
            "import pytest\n\n"
            f"def test_{function_name}_placeholder():\n"
            "    assert True\n"
        )
