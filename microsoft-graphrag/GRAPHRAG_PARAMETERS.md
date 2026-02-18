# GraphRAG Hyperparameter Tuning Guide

Complete reference for Microsoft GraphRAG hyperparameters with pros/cons and recommendations.

---

## 1. Text Chunking Parameters

### `chunking.size` (Token count per chunk)

**Default:** `1200`

| Value Range | Pros | Cons | Use Case |
|-------------|------|------|----------|
| **300-600** | • Cheaper (fewer tokens)<br>• Faster processing<br>• More granular entities | • Less context per chunk<br>• May miss relationships<br>• More chunks = more API calls | • Short documents<br>• Technical docs<br>• FAQ/Q&A content |
| **1200-1500** ✅ | • Balanced cost/quality<br>• Good context window<br>• Default recommended | • Moderate cost<br>• Moderate speed | • General use<br>• Most documents<br>• **Journey to the West** |
| **2000-3000** | • Rich context<br>• Better relationship detection<br>• Fewer chunks | • More expensive per chunk<br>• Slower processing<br>• May overwhelm entity extraction | • Academic papers<br>• Long-form narrative<br>• Complex analysis |

**Recommendation for Journey to the West:** `1500` (captures dialogue and narrative context)

---

### `chunking.overlap` (Token overlap between chunks)

**Default:** `100`

| Value Range | Pros | Cons | Use Case |
|-------------|------|------|----------|
| **0-50** | • Less redundancy<br>• Cheaper<br>• Faster | • May miss cross-chunk relationships<br>• Entities split across chunks | • Distinct sections<br>• Technical documentation |
| **100-150** ✅ | • Preserves continuity<br>• Captures cross-boundary entities<br>• Balanced redundancy | • Some token duplication<br>• Slightly higher cost | • General narrative<br>• **Default recommended** |
| **200-300** | • Maximum continuity<br>• No missed relationships | • High redundancy<br>• Expensive<br>• Duplicate entity extraction | • Dense interconnected text<br>• Legal documents |

**Recommendation for Journey to the West:** `120` (narrative continuity)

---

## 2. Entity Extraction Parameters

### `extract_graph.entity_types` (Types of entities to extract)

**Default:** `["organization", "person", "geo", "event"]`

| Configuration | Pros | Cons | Use Case |
|---------------|------|------|----------|
| **Minimal (2-3 types)**<br>`["person", "location"]` | • Faster extraction<br>• Cheaper<br>• Focused graph | • Misses important entities<br>• Less comprehensive | • Simple narratives<br>• People-focused stories |
| **Default (4 types)** ✅<br>`["organization", "person", "geo", "event"]` | • Balanced coverage<br>• General purpose<br>• Good for most content | • May miss specialized entities | • News articles<br>• Business documents<br>• General text |
| **Extended (7+ types)**<br>`["person", "geo", "event", "organization", "artifact", "creature", "concept"]` | • Comprehensive<br>• Rich knowledge graph<br>• Domain-specific | • More expensive<br>• Slower<br>• Potential noise | • **Journey to the West**<br>• Fantasy/mythology<br>• Academic research |

**Recommendation for Journey to the West:**
```yaml
entity_types: [person, geo, event, organization, artifact, creature, concept]
```
- **artifact**: Golden cudgel, magical items
- **creature**: Demons, deities, spirits
- **concept**: Buddhist/Taoist philosophy

---

### `extract_graph.max_gleanings` (Additional extraction passes)

**Default:** `1`

| Value | Pros | Cons | Cost Multiplier | Use Case |
|-------|------|------|-----------------|----------|
| **0** | • Fastest<br>• Cheapest<br>• Single pass | • May miss 20-30% of entities<br>• Lower recall | **1x** | • Budget constraints<br>• Simple documents<br>• Quick prototyping |
| **1** ✅ | • Balanced quality<br>• Catches most entities<br>• Reasonable cost | • Still misses ~10% entities | **~1.5x** | • **Default recommended**<br>• General use |
| **2** | • High recall (~95%)<br>• Comprehensive extraction | • Expensive<br>• Diminishing returns | **~2.5x** | • Critical applications<br>• Academic research |
| **3** | • Maximum recall (~98%)<br>• Exhaustive | • Very expensive<br>• Marginal improvement | **~3.5x** | • When completeness critical<br>• Small documents only |

**Recommendation for Journey to the West:** `1` (balanced - mythology is explicit)

---

## 3. Graph Clustering Parameters

### `cluster_graph.max_cluster_size` (Max entities per community)

**Default:** `10`

| Value Range | Pros | Cons | Use Case |
|-------------|------|------|----------|
| **5-8** | • Granular topics<br>• Many specific communities<br>• Detailed grouping | • Over-segmentation<br>• More communities to summarize<br>• Higher cost | • Fine-grained analysis<br>• Specific topic extraction |
| **10-12** ✅ | • Balanced granularity<br>• Reasonable community count<br>• Good default | • May group loosely related entities | • **General use**<br>• Most documents |
| **15-20** | • Broader themes<br>• Fewer communities<br>• Lower summarization cost | • May miss specific topics<br>• Coarse grouping | • **Journey to the West**<br>• Thematic analysis<br>• High-level overview |

**Recommendation for Journey to the West:** `15` (captures major mythological arcs)

---

## 4. Description Summarization Parameters

### `summarize_descriptions.max_length` (Max entity description length)

**Default:** `500`

| Value Range | Pros | Cons | Use Case |
|-------------|------|------|----------|
| **200-300** | • Concise<br>• Faster<br>• Cheaper | • May lose important details<br>• Brief descriptions | • Simple entities<br>• Budget constraints |
| **500-600** ✅ | • Detailed enough<br>• Balanced cost<br>• Default quality | • Moderate cost | • **General use**<br>• Most entities |
| **1000-1500** | • Rich descriptions<br>• Comprehensive context<br>• Better for complex entities | • More expensive<br>• Slower<br>• May include noise | • Complex domains<br>• Academic work<br>• Detailed analysis |

**Recommendation for Journey to the West:** `500` (sufficient for character descriptions)

---

## 5. Community Report Parameters

### `community_reports.max_length` (Community summary length)

**Default:** `2000`

| Value Range | Pros | Cons | Cost Impact | Use Case |
|-------------|------|------|-------------|----------|
| **1000-1500** | • Quick summaries<br>• Lower cost<br>• Faster queries | • Less detailed<br>• May miss nuances | **Low** | • Overview use cases<br>• Quick insights |
| **2000-2500** ✅ | • Comprehensive<br>• Balanced detail<br>• Good for most use | • Moderate cost<br>• Longer to read | **Medium** | • **General use**<br>• Standard analysis |
| **3000-5000** | • Very detailed<br>• Rich context<br>• Excellent for global search | • Expensive<br>• Verbose<br>• May exceed context limits | **High** | • **Journey to the West**<br>• Complex narratives<br>• Deep analysis |

**Recommendation for Journey to the West:** `3000` (complex mythology needs detail)

---

### `community_reports.max_input_length` (Max context for report generation)

**Default:** `8000`

| Value Range | Pros | Cons | Use Case |
|-------------|------|------|----------|
| **4000-6000** | • Faster<br>• Cheaper | • Limited context<br>• May miss connections | • Small communities<br>• Simple topics |
| **8000-10000** ✅ | • Balanced<br>• Good context window | • Moderate cost | • **Default recommended** |
| **12000-16000** | • Maximum context<br>• Comprehensive analysis | • More expensive<br>• Slower | • Large communities<br>• Complex topics |

---

## 6. Rate Limiting Parameters

### `requests_per_minute` (API request rate)

**Default:** `No limit (uses concurrent_requests)`

| Value Range | Pros | Cons | Use Case |
|-------------|------|------|----------|
| **1-10** | • Avoids rate limits<br>• Guaranteed success | • Very slow<br>• 40+ hours for large docs | • **Strict API limits**<br>• Free tier |
| **50-100** ✅ | • Balanced speed<br>• Safe for most quotas | • Still slower than optimal | • **Your Azure quota**<br>• Standard tier |
| **500-1000** | • Fast processing<br>• Uses full quota | • May hit burst limits<br>• Needs high quota | • Enterprise tier<br>• Large quotas |

**Your Setting:** `50` (optimized for 200k TPM Azure quota)

---

### `concurrent_requests` (Parallel API calls)

**Default:** `25`

| Value | Pros | Cons | Use Case |
|-------|------|------|----------|
| **1** | • No bursts<br>• Guaranteed no rate limits<br>• Sequential processing | • Slowest possible<br>• Underutilizes quota | • **Your case**<br>• Avoiding burst limits<br>• Conservative approach |
| **5-10** | • Moderate parallelism<br>• Reasonable speed<br>• Lower burst risk | • Some burst potential<br>• Moderate speed | • Standard quotas<br>• Balanced approach |
| **25-50** ✅ | • Fast processing<br>• Default efficiency | • Can cause bursts<br>• Needs high quota | • **High quotas only**<br>• Enterprise use |

**Your Setting:** `1` (required for Azure burst limit avoidance)

---

## 7. Advanced Parameters

### Embedding Batch Size

**Default:** `16`

| Value | Impact |
|-------|--------|
| **8** | Slower, more reliable |
| **16** ✅ | Balanced (default) |
| **32** | Faster, needs higher quota |

---

### Temperature (LLM randomness)

**Default:** `0.0` (deterministic)

| Value | Behavior | Use Case |
|-------|----------|----------|
| **0.0** ✅ | Deterministic, consistent results | **Recommended for GraphRAG** |
| **0.1-0.3** | Slight variation | Experimental |
| **0.7-1.0** | Creative, varied | Not recommended |

---

## Cost-Performance Trade-offs

### Budget Configuration (Cheapest)
```yaml
chunking.size: 600
chunking.overlap: 50
max_gleanings: 0
max_cluster_size: 8
community_reports.max_length: 1000
```
**Cost:** Low | **Quality:** Moderate | **Time:** Fast

---

### Balanced Configuration (Recommended)
```yaml
chunking.size: 1200
chunking.overlap: 100
max_gleanings: 1
max_cluster_size: 10
community_reports.max_length: 2000
```
**Cost:** Medium | **Quality:** Good | **Time:** Moderate

---

### Quality Configuration (Best Results)
```yaml
chunking.size: 1500
chunking.overlap: 150
max_gleanings: 2
max_cluster_size: 15
community_reports.max_length: 3000
entity_types: [person, geo, event, organization, artifact, creature, concept]
```
**Cost:** High | **Quality:** Excellent | **Time:** Slow

---

## Journey to the West Optimized Configuration

```yaml
# Text Processing
chunking:
  size: 1500              # Longer for narrative context
  overlap: 120            # Preserve story flow

# Entity Extraction
extract_graph:
  entity_types: [person, geo, event, organization, artifact, creature, concept]
  max_gleanings: 1        # Balanced

# Clustering
cluster_graph:
  max_cluster_size: 15    # Broader mythological themes

# Summarization
summarize_descriptions:
  max_length: 500         # Standard

community_reports:
  max_length: 3000        # Detailed for complex mythology
  max_input_length: 10000

# Rate Limiting (for your Azure quota)
completion_models:
  default_completion_model:
    requests_per_minute: 50
    tokens_per_minute: 150000
    concurrent_requests: 1
```

**Estimated Cost:** ~$4-6 for full Journey to the West
**Estimated Time:** 25-35 minutes
**Quality:** Excellent for mythological analysis

---

## Parameter Selection Decision Tree

```
1. What's your priority?
   ├─ Cost → Use Budget Configuration
   ├─ Speed → Increase concurrent_requests (if quota allows)
   └─ Quality → Use Quality Configuration

2. What's your document type?
   ├─ Short/Simple → Small chunks (600), fewer entity types
   ├─ Medium/General → Default settings
   └─ Long/Complex → Large chunks (1500+), extended entity types

3. What's your API quota?
   ├─ Low (<50k TPM) → concurrent_requests: 1, requests_per_minute: 10
   ├─ Medium (100-200k TPM) → concurrent_requests: 1-3, requests_per_minute: 50
   └─ High (500k+ TPM) → concurrent_requests: 10+, requests_per_minute: 500+

4. What's your use case?
   ├─ Quick prototype → max_gleanings: 0, small chunks
   ├─ Production system → Default balanced settings
   └─ Research/Academic → max_gleanings: 2, detailed summaries
```

---

## Monitoring and Iteration

After running GraphRAG, check:

1. **Entity Quality:** Are important entities missing? → Increase `max_gleanings` or add `entity_types`
2. **Cost:** Too expensive? → Reduce `chunk_size`, `max_gleanings`, or `max_length`
3. **Community Coherence:** Topics too broad? → Decrease `max_cluster_size`
4. **Query Quality:** Weak answers? → Increase `community_reports.max_length`

---

**Generated:** 2026-02-16
**GraphRAG Version:** 3.0.2
**Author:** Claude Code Assistant
