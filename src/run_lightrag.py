"""
run_lightrag.py
───────────────
Runs all QUESTIONS through LightRAG (naive, local, global, hybrid).
Results saved to src/results/lightrag_results.json.

Run from the project root:
    python src/run_lightrag.py
"""

import os, asyncio, json, time
import numpy as np, requests
from pathlib import Path
from dotenv import load_dotenv

ROOT         = Path(__file__).resolve().parent.parent
LIGHTRAG_DIR = ROOT / "lightrag" / "rag"
RESULTS_DIR  = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

load_dotenv(ROOT / "lightrag" / ".env")

KEY       = os.getenv("AZURE_OPENAI_API_KEY")
EMBED_URL = "https://mchen-mlpmwyb8-eastus2.cognitiveservices.azure.com/openai/deployments/text-embedding-3-large-Light-Rag/embeddings?api-version=2023-05-15"
LLM_URL   = "https://mchen-mlpmwyb8-eastus2.cognitiveservices.azure.com/openai/deployments/gpt-4o-mini-Light-Rag/chat/completions?api-version=2025-01-01-preview"

from questions import QUESTIONS
from lightrag import LightRAG, QueryParam
from lightrag.utils import EmbeddingFunc

sem              = asyncio.Semaphore(2)
last_call        = [0.0]
MIN_INTERVAL     = 0.09
llm_sem          = asyncio.Semaphore(4)
llm_last_call    = [0.0]
LLM_MIN_INTERVAL = 0.06

LIGHTRAG_MODES = ["naive", "local", "global", "hybrid"]


async def _llm(prompt, **kwargs):
    headers = {"api-key": KEY, "Content-Type": "application/json"}
    msg = [{"role": "user", "content": prompt}]
    for attempt in range(5):
        async with llm_sem:
            wait = LLM_MIN_INTERVAL - (time.time() - llm_last_call[0])
            if wait > 0:
                await asyncio.sleep(wait)
            llm_last_call[0] = time.time()
            res = requests.post(LLM_URL, headers=headers, json={"messages": msg})
        if res.status_code == 429:
            retry_after = int(res.headers.get("Retry-After", 2 ** attempt))
            print(f"  LLM 429 — waiting {retry_after}s")
            await asyncio.sleep(retry_after)
            continue
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]
    res.raise_for_status()


async def _embed(texts):
    headers = {"api-key": KEY, "Content-Type": "application/json"}
    for attempt in range(5):
        async with sem:
            wait = MIN_INTERVAL - (time.time() - last_call[0])
            if wait > 0:
                await asyncio.sleep(wait)
            last_call[0] = time.time()
            res = requests.post(EMBED_URL, headers=headers, json={"input": texts})
        if res.status_code == 429:
            retry_after = int(res.headers.get("Retry-After", 2 ** attempt))
            print(f"  Embed 429 — waiting {retry_after}s")
            await asyncio.sleep(retry_after)
            continue
        res.raise_for_status()
        return np.array([item["embedding"] for item in res.json()["data"]])
    res.raise_for_status()


async def _init_lightrag() -> LightRAG:
    rag = LightRAG(
        working_dir=str(LIGHTRAG_DIR),
        llm_model_func=_llm,
        embedding_func=EmbeddingFunc(embedding_dim=3072, max_token_size=8192, func=_embed),
        embedding_func_max_async=2,
        default_embedding_timeout=120,
    )
    await rag.initialize_storages()
    return rag


async def run_lightrag(questions: list[str]) -> dict:
    print("\n[LightRAG] Initialising …")
    rag = await _init_lightrag()
    results = {}
    for q in questions:
        results[q] = {}
        for mode in LIGHTRAG_MODES:
            print(f"  [LightRAG/{mode}]  {q[:70]}…")
            t0 = time.time()
            try:
                answer = await rag.aquery(q, param=QueryParam(mode=mode))
            except Exception as e:
                answer = f"ERROR: {e}"
            elapsed = round(time.time() - t0, 2)
            results[q][mode] = {"answer": answer, "seconds": elapsed}
            print(f"    → {elapsed:.1f}s  |  {str(answer)[:100]}")
    return results


if __name__ == "__main__":
    results = asyncio.run(run_lightrag(QUESTIONS))
    out_path = RESULTS_DIR / "lightrag_results.json"
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nResults saved → {out_path}")
