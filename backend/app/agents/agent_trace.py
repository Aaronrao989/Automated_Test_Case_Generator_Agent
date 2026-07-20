"""Agent tool registry and execution trace.

The orchestrator acts as an agent that invokes a fixed set of tools in sequence.
Each invocation is recorded (name, description, status, duration, a short
result summary) so the run is observable — surfaced in the API response and
rendered in the UI as an agent trace.
"""

import time
from contextlib import contextmanager
from typing import Any, Dict, Iterator, List

# The tools the agent can invoke, with human-readable descriptions.
TOOLS: Dict[str, str] = {
    "scan_repository": "Walk the project, detect languages, and list source files",
    "extract_functions": "Parse source into individually testable functions",
    "detect_edge_cases": "Analyze arguments and code for boundary and error conditions",
    "generate_tests": "Prompt the LLM to write pytest tests for each function",
    "execute_tests": "Run the generated tests in an isolated sandbox",
    "compute_coverage": "Measure line coverage from the test run",
}


class AgentTrace:
    """Records each tool the agent invokes during a run."""

    def __init__(self) -> None:
        self.steps: List[Dict[str, Any]] = []

    @contextmanager
    def tool(self, name: str) -> Iterator[Dict[str, Any]]:
        start = time.monotonic()
        step: Dict[str, Any] = {
            "tool": name,
            "description": TOOLS.get(name, ""),
            "status": "ok",
            "summary": "",
        }
        try:
            yield step
        except Exception as exc:  # noqa: BLE001 - recorded, then re-raised
            step["status"] = "error"
            step["summary"] = str(exc)[:200]
            raise
        finally:
            step["duration"] = round(time.monotonic() - start, 3)
            self.steps.append(step)

    def catalog(self) -> List[Dict[str, str]]:
        return [{"name": name, "description": desc} for name, desc in TOOLS.items()]
