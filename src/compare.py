"""
compare.py
──────────
Orchestrates both runners and prints a combined comparison table.
Results saved to src/results/compare_results.json.

Run from the project root:
    python src/compare.py
"""

import asyncio, json
from datetime import datetime
from pathlib import Path

from questions import QUESTIONS
from run_lightrag import run_lightrag, LIGHTRAG_MODES
from run_graphrag import run_graphrag, GRAPHRAG_METHODS

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)


def _print_summary(lr: dict, gr: dict):
    columns = [f"LR/{m}" for m in LIGHTRAG_MODES] + [f"GR/{m}" for m in GRAPHRAG_METHODS]
    q_w, c_w = 50, 10
    divider = "─" * (q_w + (c_w + 2) * len(columns))

    def _header():
        return f"{'Question':<{q_w}}" + "".join(f"  {c:>{c_w}}" for c in columns)

    for metric, label in [("seconds", "Latency (s)"), (None, "Answer length (chars)")]:
        print(f"\n{'═' * len(divider)}")
        print(label)
        print(divider)
        print(_header())
        print(divider)
        for q in QUESTIONS:
            row = f"{q[:q_w - 1]:<{q_w}}"
            for m in LIGHTRAG_MODES:
                cell = lr.get(q, {}).get(m, {})
                val = cell.get("seconds", 0) if metric else len(cell.get("answer", ""))
                row += f"  {val:>{c_w}{',.1f' if metric else ','}}"
            for m in GRAPHRAG_METHODS:
                cell = gr.get(q, {}).get(m, {})
                val = cell.get("seconds", 0) if metric else len(cell.get("answer", ""))
                row += f"  {val:>{c_w}{',.1f' if metric else ','}}"
            print(row)


async def main():
    print("=" * 60)
    print("  GraphRAG vs LightRAG — retrieval comparison")
    print("=" * 60)

    lr_results = await run_lightrag(QUESTIONS)
    gr_results = run_graphrag(QUESTIONS)

    out = {"lightrag": lr_results, "graphrag": gr_results}
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = RESULTS_DIR / f"compare_results_{timestamp}.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nFull results saved → {out_path}")

    _print_summary(lr_results, gr_results)


if __name__ == "__main__":
    asyncio.run(main())
