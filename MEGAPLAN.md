# MEGAPLAN — From-Scratch Evaluation Plan

## Project Goal (Restated)

**Compare different RAG retrieval approaches and methodologies for legal documents.**

Not building a product. Not building an agent. Not fine-tuning models. Comparing
off-the-shelf retrieval approaches on legal text to see what works, what doesn't,
and why. The output is a research paper with reproducible numbers.

## What We Are Testing

Six research questions, each isolating one design choice:

| RQ | Question | What varies | What stays fixed |
|----|----------|-------------|------------------|
| RQ1 | Does chunking help or hurt legal retrieval? | Chunking strategy | BM25, direct query, no rerank |
| RQ2 | BM25 vs Dense vs Hybrid — which is best? | Retrieval method | Best chunking from RQ1, direct query, no rerank |
| RQ3 | Does cross-encoder reranking help? | Reranker on/off | Best pipeline from RQ1-2 |
| RQ4 | RRF vs weighted fusion for hybrid? | Fusion method | Best pipeline otherwise |
| RQ5 | Do results transfer to a different legal corpus? | Dataset | Best pipeline, on LegalBench-RAG |
| RQ6 | Does query transformation help? | Query strategy | Best retrieval, best chunking, no rerank |

**RQ6 (query transformation) is benched** — deferred to later. LLM calls are
~20s each, making it expensive to run at scale. We'll revisit after the core
retrieval comparison (RQ1-4) is solid.

## What We Are NOT Testing (and why)

| Excluded | Reason |
|----------|--------|
| Multiple embedding models | One strong model (BGE) is enough — comparing models is a different paper |
| Fine-tuned models | We compare off-the-shelf approaches, not trained models |
| Graph neural networks | Requires training infrastructure, out of scope for a retrieval comparison |
| Query decomposition / multi-query | Too complex, adds confounds, not standard for legal retrieval |
| Iterative / agentic retrieval | Separate concern from single-pass retrieval comparison |
| LLM-based reranking (GPT-4) | Cost-prohibitive, and the IL-PCSR paper already shows it works |
| Semantic chunking with LLMs | Requires LLM calls per document, cost-prohibitive at scale |
| Summary-augmented chunking | Promising but requires LLM summarization of every doc — future work |

## Dataset: IL-PCSR (Primary)

From the paper (EMNLP 2025):
- **936 statutes** (avg 650 words) — short, technical, abstract
- **3,183 precedents** (avg 7,485 words) — long, narrative, lexically similar to queries
- **627 dev queries** (avg 3,383 words) — long case judgment descriptions
- **627 test queries** — held out for final evaluation

Two tasks:
- **LSR (Legal Statute Retrieval):** query → relevant statutes (avg 2.69 relevant per query)
- **PCR (Prior Case Retrieval):** query → relevant precedents (avg 3.87 relevant per query)

Key paper finding to reproduce: **BM25 dominates PCR, dense dominates LSR.**
This asymmetry is the most interesting result and the main argument for hybrid.

## Metrics (Matching IL-PCSR Paper)

The paper uses:
- **macro-F1@k** — primary metric (best k selected on dev, evaluated on test)
- **MAP** (Mean Average Precision) — secondary
- **MRR** (Mean Reciprocal Rank) — secondary

We also report (standard IR metrics, for comparability with other work):
- **Recall@k** — what fraction of relevant docs are in top-k
- **NDCG@k** — ranking quality
- **Precision@k** — what fraction of top-k are relevant

We do NOT invent new metrics. We use exactly what the paper uses so our numbers
are directly comparable.

## BM25 Implementation (Critical Fix)

The IL-PCSR authors use **scikit-learn TfidfVectorizer with sparse matrix operations**
(their `utils/bm25.py`). This is fast because it uses scipy sparse matrices, not
Python loops. We must do the same.

Options:
1. `bm25s` library — 500x faster than rank-bm25, sparse matrix based, pip install
2. Replicate IL-PCSR's sklearn approach — proven, matches their numbers exactly

**Decision: Use `bm25s`.** It's a well-tested library, achieves the same sparse
matrix approach, and is pip-installable. If numbers don't match the paper, we
fall back to replicating their exact sklearn code.

BM25 hyperparameters from the paper: `b=0.7, k1=1.6`, n-grams (1-5).

## Hybrid Fusion (Critical Fix)

Current implementation: weighted score normalization. This is wrong.

From the research:
- **RRF** (Reciprocal Rank Fusion): safe default, no parameters, rank-based
- **Weighted (convex combination)**: can outperform RRF by ~8 points with proper
  normalization and tuned alpha, but requires dev set tuning
- The IL-PCSR paper uses weighted alpha (grid search or dynamic)

**Decision: Test BOTH RRF (k=60) and weighted (alpha tuned on dev).**
This is RQ5. RRF is the zero-shot baseline; weighted is the tuned baseline.

## Query Transformation (RQ6 — Benched/Deferred)

From the research:
- "Not All Queries Need Rewriting" paper: rewriting **degrades** performance by 9%
  on FiQA, **improves** by 5% on TREC-COVID, **no effect** on SciFact. It's
  domain-dependent.
- Degradation happens when rewriting substitutes domain-specific terms that
  already match well (reduces lexical alignment).
- HyDE helps when there's a vocabulary mismatch between query and document.
- For IL-PCSR: queries are very long (3,383 words avg). Rewriting a 3,383-word
  legal judgment into a "better search query" may lose important legal terminology.
- GuRE (trained query rewriter for legal) helps, but we're testing off-the-shelf
  methods, not trained rewriters.

**Deferred because:** LLM calls are ~20s each. Running 627 queries × 4 strategies
× 2 tasks = ~28 hours of API calls. Not worth it until the core retrieval
comparison (RQ1-4) is solid and we know which pipeline to apply it to.

**When we revisit:**
1. Direct — no transformation (baseline)
2. Keyword expansion — rule-based, adds legal synonyms (already implemented)
3. LLM query rewrite — Gemini rewrites query for retrieval (already implemented)
4. HyDE — Gemini generates hypothetical legal passage (already implemented)

Run on 50-query stratified subset, compare against direct baseline.

## Evaluation Protocol

For every experiment:
1. **Smoke test** — run on 10 queries, verify it completes in <2 min, check
   output format is correct
2. **Dev run** — run on full 627 dev queries (for non-LLM experiments) or
   50-query stratified subset (for LLM experiments)
3. **Record** — macro-F1@k, MAP, MRR, recall@k, NDCG@k, precision@k, latency
4. **Compare** — delta against baseline (BM25 whole-doc direct, the Stage A baseline)

## Staged Execution Order

```
Stage 0: Fix infrastructure
  ├── Install bm25s, replace hand-rolled BM25
  ├── Add RRF fusion to hybrid retriever
  ├── Add macro-F1@k and MAP metrics
  ├── Add per-query progress printing (done)
  ├── Fix output file naming (done)
  └── Write/update tests for all new code

Stage A: BM25 baseline (RQ1 partial)
  ├── Smoke test: 10 queries, statute task, BM25 whole-doc
  ├── Full dev: 627 queries × 2 tasks × BM25 whole-doc
  └── Target: reproduce paper's ~13-18% F1 (LSR), ~25-33% F1 (PCR)

Stage B: Dense retrieval (RQ2 partial)
  ├── Smoke test: 10 queries, dense (BGE via MLX)
  ├── Full dev: 627 queries × 2 tasks
  └── Expected: dense > BM25 for LSR, dense < BM25 for PCR

Stage C: Hybrid retrieval (RQ2 + RQ4)
  ├── Smoke test: 10 queries, hybrid RRF
  ├── Full dev: RRF (k=60) and weighted (alpha tuned on dev)
  └── Expected: hybrid > both individual methods

Stage D: Chunking ablation (RQ1)
  ├── Smoke test: 10 queries × 3 chunking strategies
  ├── Full dev: whole vs fixed-512 vs recursive-512
  └── Expected: chunking hurts statutes (short), may help precedents (long)

Stage E: Reranking (RQ3)
  ├── Smoke test: 10 queries, cross-encoder on top-20 candidates
  ├── Subset: 100 queries (cross-encoder is ~100ms per pair)
  └── Expected: marginal improvement, high latency cost

Stage F: LegalBench-RAG (RQ5)
  ├── Best pipeline from Stages A-E
  └── Snippet-level precision/recall at character level

Stage G: Query transformation (RQ6 — BENCHED, revisit later)
  ├── Smoke test: 10 queries × 4 query strategies
  ├── Subset: 50 queries × 4 strategies (LLM calls ~20s each)
  └── Expected: rewrite hurts PCR, may help LSR

Stage H: Final test evaluation
  ├── Best pipeline on test split (627 queries)
  └── Report final numbers with statistical significance
```

## Test Updates Required

For every new component, write a test:
- `test_bm25s.py` — verify bm25s integration, check scores match expected
- `test_rrf.py` — verify RRF fusion produces correct rankings
- `test_metrics.py` — verify macro-F1@k and MAP calculations
- `test_query_strategies.py` — verify LLM rewrite and HyDE produce valid output
- `test_smoke.py` — 10-query end-to-end pipeline test (fast, <30s)

Every test must run in <30s. If a test requires an LLM call, mock it or skip
in CI.
