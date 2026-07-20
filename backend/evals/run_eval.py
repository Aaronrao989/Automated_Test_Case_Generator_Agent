"""Evaluation harness for the test generator.

Runs the pipeline against a small golden dataset and scores it on the four
things the rubric cares about:

  * relevance  — did we extract the functions we expected?
  * generation — did we produce tests for them?
  * pass-rate  — do the generated tests execute and pass? (LLM mode only)
  * coverage   — average line coverage of the generated tests (LLM mode only)

Usage (from the backend/ directory):

    python -m evals.run_eval

With a real ``GROQ_API_KEY`` set you get full pass-rate/coverage scoring; in
offline "demo" mode only relevance/generation are meaningful, so the gate is
relaxed accordingly. Exit code is non-zero if the run falls below threshold
(useful as a CI check).
"""

import json
import sys
from pathlib import Path

from app.agents.orchestrator import TestGenerationOrchestrator
from app.core.config import settings

GOLDEN = Path(__file__).parent / "golden.json"
RELEVANCE_GATE = 1.0      # every expected function must be found
GENERATION_GATE = 1.0     # every case must yield at least one test
PASS_RATE_GATE = 0.8      # LLM mode: >=80% of test modules pass


def _run_case(case: dict) -> dict:
    orchestrator = TestGenerationOrchestrator()
    result = orchestrator.analyze_from_text(case["code"])

    found = {f["name"] for f in result["structure"]["functions"]}
    expected = set(case["expect_functions"])
    relevance = len(expected & found) / len(expected)

    tests = result.get("tests", [])
    generated = bool(tests)

    test_results = result.get("test_results", [])
    passed = sum(1 for r in test_results if r.get("status") == "passed")
    pass_rate = (passed / len(test_results)) if test_results else 0.0

    coverage = result.get("coverage", {})
    return {
        "id": case["id"],
        "relevance": relevance,
        "generated": generated,
        "pass_rate": pass_rate,
        "coverage": coverage.get("total_coverage", 0.0),
        "executed": coverage.get("executed", False),
    }


def main() -> int:
    cases = json.loads(GOLDEN.read_text())
    live = settings.has_groq_key
    mode = "LLM" if live else "demo (offline)"
    print(f"\nRunning eval on {len(cases)} golden cases — mode: {mode}\n")
    print(f"{'case':<12}{'relevance':>10}{'tests':>8}{'pass%':>8}{'cov%':>8}")
    print("-" * 46)

    rows = [_run_case(c) for c in cases]
    for r in rows:
        print(
            f"{r['id']:<12}{r['relevance']*100:>9.0f}%{'yes' if r['generated'] else 'no':>8}"
            f"{r['pass_rate']*100:>7.0f}%{r['coverage']:>7.0f}%"
        )

    relevance = sum(r["relevance"] for r in rows) / len(rows)
    generation = sum(1 for r in rows if r["generated"]) / len(rows)
    executed_rows = [r for r in rows if r["executed"]]
    pass_rate = (
        sum(r["pass_rate"] for r in executed_rows) / len(executed_rows)
        if executed_rows
        else 0.0
    )
    avg_cov = (
        sum(r["coverage"] for r in executed_rows) / len(executed_rows)
        if executed_rows
        else 0.0
    )

    print("-" * 46)
    print(f"relevance:  {relevance*100:.0f}%")
    print(f"generation: {generation*100:.0f}%")
    if live:
        print(f"pass-rate:  {pass_rate*100:.0f}%")
        print(f"coverage:   {avg_cov:.0f}%")

    # Gate: relevance + generation always; pass-rate only in LLM mode.
    ok = relevance >= RELEVANCE_GATE and generation >= GENERATION_GATE
    if live:
        ok = ok and pass_rate >= PASS_RATE_GATE

    print(f"\nRESULT: {'PASS ✅' if ok else 'FAIL ❌'}\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
