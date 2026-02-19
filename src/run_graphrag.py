"""
run_graphrag.py
───────────────
Runs all QUESTIONS through GraphRAG (local + global) via CLI subprocess.
Results saved to src/results/graphrag_results.json.

Run from the project root:
    python src/run_graphrag.py
"""

import sys, subprocess, json, time
from pathlib import Path

ROOT         = Path(__file__).resolve().parent.parent
GRAPHRAG_DIR = ROOT / "microsoft-graphrag"
RESULTS_DIR  = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

from questions import QUESTIONS

GRAPHRAG_METHODS = ["local", "global"]


def _graphrag_query(question: str, method: str) -> tuple[str, float]:
    """Run a single graphrag CLI query and return (answer, elapsed_seconds)."""
    cmd = [
        sys.executable, "-m", "graphrag", "query",
        "--root", str(GRAPHRAG_DIR),
        "--method", method,
        question,
    ]
    t0 = time.time()
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=None,
        )
        elapsed = round(time.time() - t0, 2)
        if proc.returncode != 0:
            return f"ERROR (exit {proc.returncode}): {proc.stderr.strip()[:200]}", elapsed
        output = proc.stdout.strip()
        for marker in ("SUCCESS: Local Search Response:", "SUCCESS: Global Search Response:", "Answer:"):
            if marker in output:
                output = output.split(marker, 1)[-1].strip()
                break
        return output, elapsed
    except FileNotFoundError:
        return "ERROR: graphrag not installed (run: pip install graphrag)", 0.0


def run_graphrag(questions: list[str]) -> dict:
    print("\n[GraphRAG] Running CLI queries …")
    results = {}
    for q in questions:
        results[q] = {}
        for method in GRAPHRAG_METHODS:
            print(f"  [GraphRAG/{method}]  {q[:70]}…")
            answer, elapsed = _graphrag_query(q, method)
            results[q][method] = {"answer": answer, "seconds": elapsed}
            print(f"    → {elapsed:.1f}s  |  {str(answer)[:100]}")
    return results


if __name__ == "__main__":
    results = run_graphrag(QUESTIONS)
    out_path = RESULTS_DIR / "graphrag_results.json"
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nResults saved → {out_path}")
