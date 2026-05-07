# GraphRAG vs LightRAG

A side-by-side benchmark of Microsoft GraphRAG and LightRAG on the same corpus, evaluated with RAGAS. The headline finding: LightRAG indexed 3-5x faster and cost 50-70% less to operate, with answer quality close enough to GraphRAG that the cost difference dominates the choice for most workloads.

## What's in this repo

| Path | What it is |
|---|---|
| `microsoft-graphrag/` | GraphRAG pipeline configured against the corpus |
| `lightrag/` | LightRAG pipeline configured against the same corpus |
| `src/` | Shared chunking, ingestion, and evaluation code |
| `Journey to the West - Wu Cheng_en 1592.pdf` | The benchmark corpus (~1.6M words, ~20K chunks at default chunk size) |

## Why these two

| | GraphRAG (Microsoft) | LightRAG |
|---|---|---|
| Graph construction | Hierarchical communities via Leiden clustering | Entity + relation pairs, no community summarization |
| Indexing cost | High (multiple LLM passes per chunk) | Low (one pass for entities, one for relations) |
| Query strategy | Local + global query modes | Hybrid keyword + entity-graph |
| Best for | Sense-making across a whole corpus | Targeted Q&A with cost discipline |

LightRAG removes the community-summarization step that drives most of GraphRAG's indexing cost. The benchmark question: how much answer quality do you give up for that?

## Benchmark setup

- **Corpus:** *Journey to the West* (1592, Wu Cheng'en) — chosen because it has dense entity relationships (100+ named characters across 100 chapters) that stress entity-graph builders
- **Chunking:** ~1,000-token chunks, ~200-token overlap, ~20K chunks total
- **Eval framework:** RAGAS (faithfulness, answer relevancy, context precision)
- **Evaluation environment:** Azure AI Foundry
- **LLM:** GPT-4o-mini for both pipelines (held constant)

## Results

| Metric | GraphRAG | LightRAG | Delta |
|---|---|---|---|
| Indexing time | baseline | **3-5x faster** | LightRAG wins |
| Indexing cost | baseline | **50-70% lower** | LightRAG wins |
| Answer quality (RAGAS) | comparable | comparable | within noise |

The cost gap comes almost entirely from GraphRAG's community summarization phase, which adds ~N log N LLM calls on top of the entity extraction pass.

## When to pick which

- **GraphRAG** when you need *global* questions ("what are the recurring themes?"). Community summaries help here.
- **LightRAG** when most queries are *local* ("who is X and what is their relationship to Y?"). Entity-graph retrieval is enough.

## Run it locally

```bash
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Index with GraphRAG
cd microsoft-graphrag && python -m graphrag.index --root .

# Index with LightRAG
cd ../lightrag && python index.py

# Run RAGAS eval
cd ../src && python evaluate.py
```

Set `OPENAI_API_KEY` (or Azure equivalents) in `.env` before running either pipeline.

## Stack

Microsoft GraphRAG · LightRAG · RAGAS · Azure AI Foundry · GPT-4o-mini
