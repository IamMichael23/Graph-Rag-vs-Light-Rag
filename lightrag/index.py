import os, asyncio, numpy as np, time, requests
from lightrag import LightRAG, QueryParam
from lightrag.utils import EmbeddingFunc
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

KEY = os.getenv("AZURE_OPENAI_API_KEY")
ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
LLM = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# Direct URLs - bypasses SDK routing issues
EMBED_URL = "https://mchen-mlpmwyb8-eastus2.cognitiveservices.azure.com/openai/deployments/text-embedding-3-large-Light-Rag/embeddings?api-version=2023-05-15"
LLM_URL  = "https://mchen-mlpmwyb8-eastus2.cognitiveservices.azure.com/openai/deployments/gpt-4o-mini-Light-Rag/chat/completions?api-version=2025-01-01-preview"

# Embedding: 2 concurrent, 0.09s apart => ~667 RPM (limit: 720)
sem = asyncio.Semaphore(2)
last_call = [0.0]
MIN_INTERVAL = 0.09

# LLM: 4 concurrent, 0.06s apart => ~800 RPM (limit: 1000)
llm_sem = asyncio.Semaphore(4)
llm_last_call = [0.0]
LLM_MIN_INTERVAL = 0.06

async def llm(prompt, **kwargs):
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
            print(f"  LLM 429 — waiting {retry_after}s (attempt {attempt+1}/5)")
            await asyncio.sleep(retry_after)
            continue
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]
    res.raise_for_status()

async def embed(texts):
    headers = {"api-key": KEY, "Content-Type": "application/json"}
    for attempt in range(5):
        async with sem:                          # release sem before any long sleep
            wait = MIN_INTERVAL - (time.time() - last_call[0])
            if wait > 0:
                await asyncio.sleep(wait)
            last_call[0] = time.time()
            res = requests.post(EMBED_URL, headers=headers, json={"input": texts})
        if res.status_code == 429:               # sleep OUTSIDE sem
            retry_after = int(res.headers.get("Retry-After", 2 ** attempt))
            print(f"  429 rate limit — waiting {retry_after}s (attempt {attempt+1}/5)")
            await asyncio.sleep(retry_after)
            continue
        res.raise_for_status()
        return np.array([item["embedding"] for item in res.json()["data"]])
    res.raise_for_status()

async def init():
    rag = LightRAG(
        working_dir="./rag",
        llm_model_func=llm,
        embedding_func=EmbeddingFunc(embedding_dim=3072, max_token_size=8192, func=embed),
        embedding_func_max_async=2,   # match semaphore above
        default_embedding_timeout=120, # worker timeout = 120*2 = 240s, survives long Retry-After waits
    )
    await rag.initialize_storages()
    return rag

# Index the text - FULL BOOK (with 600 RPM should take ~10-15 min)
rag = asyncio.run(init())
text = open("../shared-data/Journey to the West.txt", encoding="utf-8").read()
print(f"Indexing {len(text):,} characters (FULL - faster with 600 RPM)...")
rag.insert(text)
print("Done!")
