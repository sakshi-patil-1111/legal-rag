# Legal RAG — Project Plan and Status

## Overview

Modular, reproducible experimental framework for evaluating retrieval and agentic RAG strategies on legal case analysis and decision support.

Primary research question: **How do different design choices in a legal RAG pipeline affect retrieval quality and downstream legal decision support?**

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[nn,retrieval,dev]"
pip install datasets huggingface_hub
```

## Running

```bash
# Phase 0: tiny fixture smoke test
python scripts/run_phase0.py

# Phase 1: IL-PCSR (fixture or real data)
python scripts/run_phase1.py                      # fixture
python scripts/run_phase1.py phase1_il_pcsr.json  # real data

# Phase 2: LegalBench-RAG
python scripts/run_phase2.py                                      # fixture
python scripts/run_phase2.py phase2_legalbench_rag_privacy_qa.json # privacy_qa subset
python scripts/run_phase2.py phase2_legalbench_rag.json            # full

# Tests
pytest tests/ -q
```

## Data

Datasets are downloaded via scripts and stored in `data/raw/` (gitignored).

- **IL-PCSR**: `python scripts/download_il_pcsr.py` (requires HF_TOKEN in .env, gated dataset)
- **LegalBench-RAG**: download from Dropbox (see scripts or README)

Fixtures for engineering tests live in `data/fixtures/`.

## Benchmark Phases

### Phase 0: Tiny Local Fixture — DONE
Engineering validation of the full pipeline on synthetic data.

### Phase 1: IL-PCSR — IN PROGRESS
Primary development benchmark. Indian legal statute + precedent retrieval.
- 627 test queries, 936 statute candidates, 3,183 precedent candidates
- Two tasks: statute retrieval (Task A) and precedent retrieval (Task B)
- Data downloaded, adapter works, BM25 baseline ready

**Not yet set up:**
- Real sentence-transformer dense retriever (current "dense" is TF-IDF/SVD placeholder)
- LLM-based query rewriting and HyDE (current implementations are static stubs)
- Cross-encoder reranker (only token-overlap Jaccard exists)
- NDCG and Precision@k metrics
- Index persistence and caching
- Reproducibility metadata (experiment ID, timestamp, git commit, seed)
- Dev/test split discipline (currently runs on test directly)
- Staged ablation scripts (compare_grid.py does forbidden Cartesian product)

### Phase 2: LegalBench-RAG — IN PROGRESS
External validation benchmark. US legal contract retrieval.
- 6,889 queries across 4 sub-benchmarks (contractnli, cuad, maud, privacy_qa)
- 714 corpus documents, snippet-level ground truth with char spans
- Data downloaded, adapter preserves snippet-level GT, dual eval mode (document + snippet)

**Not yet set up:**
- Same infrastructure gaps as Phase 1
- Stratified development subset for expensive experiments

### Phase 3: AIBE — NOT STARTED
Downstream Indian legal QA. Compare only shortlisted systems from Phase 1-2.

### Phase 4: BhashaBench-Legal — NOT STARTED
Optional large-scale validation. Only if Phase 1-3 stable.

### Phase 5: Advanced Decision-Support — NOT STARTED
Optional. IL-TUR, NyayaRAG-style evaluation.

## Staged Ablation Methodology (Part 12)

Do NOT run full Cartesian products. Use staged ablation:

- **Stage A**: Fix retrieval to BM25. Test whole-doc vs fixed chunking vs recursive chunking.
- **Stage B**: Fix strongest representation. Test BM25 vs dense vs hybrid.
- **Stage C**: Fix strongest retrieval. Test direct vs rewrite vs HyDE.
- **Stage D**: Fix strongest pipeline. Test no reranking vs cross-encoder.
- **Stage E**: Build constrained agentic controller using strongest components.

## Architecture

```
Dataset → Parser → Chunker → Index → Query Strategy → Retriever → Reranker → Evaluation → Results
```

Each component is replaceable via abstract base classes:
- `Chunker` (chunking.py)
- `Retriever` (retrievers/base.py) — supports both `search()` (doc-level) and `search_chunks()` (chunk-level)
- `QueryStrategy` (query.py)
- `Reranker` (reranker.py)

## Infrastructure Gaps (Priority Order)

1. NDCG + Precision@k metrics
2. Reproducibility metadata in results
3. Real sentence-transformer dense retriever
4. Index persistence and caching
5. Dev/test split discipline
6. Staged ablation scripts
7. Cross-encoder reranker
8. LLM-based query rewriting + HyDE
