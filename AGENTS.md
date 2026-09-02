# Legal RAG — Project Plan

## Goal

Compare different RAG retrieval approaches for legal documents.
Focus on one dataset (IL-PCSR), establish baselines, then ablate one variable at a time.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[nn,retrieval,dev]"
pip install datasets huggingface_hub bm25s sentence-transformers
```

## Running

```bash
# Download IL-PCSR (requires HF_TOKEN in .env)
python scripts/download_il_pcsr.py

# Run an experiment
python scripts/run_phase1.py configs/stage_a_bm25.json

# Tests
pytest tests/ -q
```

## Data

- **IL-PCSR**: `data/raw/il_pcsr/` (gitignored, downloaded via script)
  - 936 statutes, 3,183 precedents, 627 dev / 627 test queries
  - Two tasks: statute retrieval (LSR), precedent retrieval (PCR)
- Fixtures: `data/fixtures/` (for unit tests)

## Research Questions

| RQ | Question | Status |
|----|----------|--------|
| RQ1 | Chunking: whole vs fixed vs recursive | Pending |
| RQ2 | BM25 vs Dense vs Hybrid | Stage A/B done, C pending |
| RQ3 | Cross-encoder reranking on/off | Pending |
| RQ4 | RRF vs weighted fusion | Pending |
| RQ5 | Transfer to LegalBench-RAG | Later |
| RQ6 | Query transformation (rewrite/HyDE) | Benched |

## Staged Execution

```
Stage 0: Infrastructure (bm25s, RRF, metrics, tests)     DONE
Stage A: BM25 baseline                                    DONE
Stage B: Dense (BGE-small + legal fine-tuned)             IN PROGRESS
Stage C: Hybrid (RRF + weighted)                          Pending
Stage D: Chunking ablation                                Pending
Stage E: Reranking                                        Pending
Stage F: LegalBench-RAG transfer                          Later
Stage G: Query transformation                             Benched
Stage H: Final test evaluation                            Pending
```

## Architecture

```
Dataset → Chunker → Retriever → [Reranker] → Evaluator → Results
```

Components (all replaceable via config):
- **Chunkers**: WholeDocument, FixedToken, FixedChar, Recursive
- **Retrievers**: BM25 (bm25s), Dense (BGE via MLX/ST), Hybrid (RRF)
- **Rerankers**: NoOp, TokenOverlap, CrossEncoder
- **Query strategies**: Direct, KeywordExpansion, LLMRewrite, HyDE (benched)
- **Metrics**: recall@k, precision@k, ndcg@k, f1@k, mrr, map

## Metrics

Matching IL-PCSR paper: macro-F1@k, MAP, MRR (primary).
Also: recall@k, precision@k, NDCG@k (for comparability).

## Configs

Only `configs/stage_*.json` — one per experiment. Old phase configs deleted.

## Key Findings So Far

- BM25 beats off-the-shelf dense (BGE-small) on both LSR and PCR
- This contradicts the paper, but the paper uses fine-tuned legal models
- Testing a legal fine-tuned model (axondendriteplus/Legal-Embed-bge-base) to see if it closes the gap
- bm25s is ~500x faster than hand-rolled BM25 (12s vs 45min for 627 queries)

## Principles

- One dataset, one variable at a time
- Smoke test on 10 queries before full run
- Always update tests
- Minimal code, no verbosity
- Reproducibility (seed, git commit, config hash in results)
