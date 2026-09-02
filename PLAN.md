# Evaluation Plan — Revised After Research

## What I Got Wrong

1. **Hand-rolled BM25 in pure Python** — 45+ minutes for 627 queries × 3,183 docs. The IL-PCSR authors themselves use scikit-learn's `TfidfVectorizer` with sparse matrix operations (their `utils/bm25.py`). The `bm25s` library achieves 500x speedup over rank-bm25 by eagerly computing scores into sparse matrices. I should use `bm25s` or replicate the IL-PCSR authors' sklearn approach.

2. **No clear experimental design** — I was running configs ad hoc without a defined ablation structure. The `rag-ablations` package and the "Beyond the Reranker" paper show the right pattern: always state the BM25 baseline, measure every design choice as a delta against it, and report statistical significance.

3. **Confused about what we're testing** — I built LLM query rewrite, HyDE, cross-encoder reranker, etc. without first establishing baselines. The literature is clear: establish BM25 baseline first, then dense, then hybrid, then add components one at a time measuring the delta.

4. **Wrong metrics for IL-PCSR** — The IL-PCSR paper uses **macro-F1@k, MAP, and MRR** (not NDCG). They select best k on dev set, then evaluate on test. I was using recall@k, precision@k, NDCG, and MRR. I need to add macro-F1@k and MAP to match their methodology for comparability.

5. **No RRF for hybrid** — The literature is unanimous: hybrid retrieval should use Reciprocal Rank Fusion (RRF), not score normalization. RRF is rank-based, doesn't need score calibration, and is the production standard. My hybrid retriever uses weighted score normalization which is known to be inferior.

6. **Tried to run everything at once** — Should have run Stage A (BM25 baseline) first, verified it works and matches the paper's numbers, then proceeded stage by stage.

---

## What We're Testing (Core Research Questions)

### RQ1: Chunking Strategy
Does chunking help or hurt for legal documents?
- IL-PCSR: statutes are short (avg 650 words), precedents are long (avg 7,485 words). Chunking may help precedents but hurt statutes.
- LegalBench-RAG: snippet-level evaluation means chunking directly affects whether we can locate the exact relevant span.
- **Compare:** whole-doc vs fixed-512 vs recursive-512 vs semantic chunking

### RQ2: Retrieval Method
BM25 vs Dense vs Hybrid — which is best for legal text?
- IL-PCSR paper finding: BM25 dominates for PCR (precedents), dense dominates for LSR (statutes). This is a key result to reproduce.
- LegalBench-RAG: snippet-level precision/recall at character level.
- **Compare:** BM25 (bm25s) vs Dense (BGE via MLX) vs Hybrid (RRF fusion)

### RQ3: Query Transformation
Does LLM-based query rewriting or HyDE improve retrieval?
- Legal queries are long (avg 3,383 words for IL-PCSR). Rewriting may help or may lose important legal terminology.
- HyDE generates a hypothetical legal document — may help for statutes (abstract language) but hurt for precedents (lexical match matters).
- **Compare:** direct vs keyword-expansion vs LLM-rewrite vs HyDE (on a stratified subset due to API cost)

### RQ4: Reranking
Does cross-encoder reranking improve over first-stage retrieval?
- The "Beyond the Reranker" paper finds a strong cross-encoder accounts for most pipeline quality. But `rag-ablations` finds cross-encoder reranking was NOT worth it (0.0013 nDCG improvement, 200x slower).
- Legal domain may differ — legal text has precise terminology where cross-encoders can help.
- **Compare:** no rerank vs cross-encoder (ms-marco-MiniLM) vs cross-encoder (legal-domain if available)

### RQ5: Hybrid Fusion Strategy
RRF vs weighted score normalization?
- RRF is the production standard (rank-based, no calibration needed).
- Weighted sum requires tuning alpha — the IL-PCSR paper does grid search over alpha.
- **Compare:** RRF (k=60) vs weighted sum (alpha=0.5) vs dynamic alpha

---

## Corrected Pipeline Architecture

Based on the research, the standard RAG retrieval pipeline is:

```
Query → [Query Transform] → [BM25 + Dense parallel retrieval] → [RRF Fusion] → [Cross-encoder Rerank] → Final Results
```

Each stage is an ablation point. We measure the delta from adding/removing each component.

---

## Staged Evaluation Plan

### Stage 0: Fix Infrastructure (PREREQUISITE)
- Replace hand-rolled BM25 with `bm25s` library (or sklearn sparse approach)
- Add RRF fusion to hybrid retriever
- Add macro-F1@k and MAP metrics (to match IL-PCSR paper)
- Add per-query progress printing (already done)
- Fix output file naming (already done)

### Stage A: BM25 Baseline (IL-PCSR)
- Whole-doc, BM25, direct query, no rerank
- Both tasks: statute (LSR) and precedent (PCR)
- Dev split (627 queries)
- **Target to reproduce:** BM25 full-doc ~13-18% F1 for LSR, ~25-33% F1 for PCR
- This validates our BM25 implementation against the paper

### Stage B: Dense Retrieval (IL-PCSR)
- Whole-doc, Dense (BGE-small via MLX), direct query, no rerank
- Both tasks
- Compare against Stage A baseline
- **Expected:** Dense > BM25 for LSR, Dense < BM25 for PCR (per paper)

### Stage C: Hybrid Retrieval (IL-PCSR)
- Whole-doc, Hybrid (BM25 + Dense with RRF), direct query, no rerank
- Both tasks
- Compare against Stage A and B
- **Expected:** Hybrid > both individual methods

### Stage D: Chunking Ablation (IL-PCSR)
- BM25 only (fastest), compare: whole vs fixed-512 vs recursive-512
- Both tasks
- Measure impact of chunking on retrieval quality

### Stage E: Reranking (IL-PCSR, subset)
- Best retriever from Stage C + cross-encoder reranker
- Stratified 100-query subset (cross-encoder is slow)
- Compare with and without reranking

### Stage F: Query Transformation (IL-PCSR, subset)
- Best retriever + LLM query rewrite / HyDE
- Stratified 50-query subset (LLM calls are ~20s each)
- Compare direct vs rewrite vs HyDE

### Stage G: LegalBench-RAG (snippet-level)
- Best pipeline from Stages A-F
- Snippet-level precision/recall at character level
- Different corpus (contracts, not case law)

---

## Key Implementation Changes Needed

1. **BM25**: Use `bm25s` library (`pip install bm25s`) — 500x faster, sparse matrix based
2. **Hybrid**: Add RRF fusion (`score = 1/(k + rank)` for each retriever, sum, re-rank)
3. **Metrics**: Add `macro_f1@k` and `map` (mean average precision) to match IL-PCSR paper
4. **Progress**: Print per-query progress with ETA (already done)
5. **Output**: Use experiment_name in filenames (already done)
6. **Dev/test split**: Tune on dev, evaluate final on test (already configured)
