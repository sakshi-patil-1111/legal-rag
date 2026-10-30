# Legal RAG Project

Reproducible experimental framework for comparing retrieval strategies on legal
case analysis. Currently focused on the IL-PCSR benchmark (Indian statute and
precedent retrieval). See `report.tex` for the write-up.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[nn,retrieval,dev]"
pip install datasets huggingface_hub
```

## Data Download

```bash
# IL-PCSR (gated, requires HF_TOKEN in .env)
python scripts/download_il_pcsr.py
```

## Running

Experiments are config-driven:

```bash
python scripts/run_phase1.py <config_name>.json

# Examples
python scripts/run_phase1.py stage_a_bm25.json        # BM25 whole-doc baseline
python scripts/run_phase1.py stage_d_recursive.json   # BM25 + recursive-512 chunking
python scripts/run_phase1.py stage_b2_qwen3_chunked.json
```

Configs live in `configs/`. Results are written to `results/<stage>/` —
aggregated summaries are committed, per-query outputs are gitignored.

| Stage | Comparison |
|-------|-----------|
| A | BM25 whole-document baseline |
| B | Dense retrievers (BGE, Legal-Embed, SAILER) |
| B2 | Qwen3-Embedding-0.6B (long-context dense) |
| C | Hybrid BM25 + dense via RRF |
| D | Chunking ablation (whole / fixed-512 / recursive-512) |
| E | Cross-encoder reranking |
| H | Final test-split evaluation |

For long-context dense models on limited GPU memory, queries can be truncated
via `retrieval.max_length` and index/query encoding can be split across
devices with `device` / `query_device`. The Qwen3 LSR run was executed on a
Kaggle T4 (fp16, queries capped at 2048 tokens).

## Headline results (dev split, 627 queries)

| Method | LSR F1@10 | LSR MAP | PCR F1@10 | PCR MAP |
|--------|-----------|---------|-----------|---------|
| BM25 whole-doc | 8.4% | 9.6% | 11.0% | 18.4% |
| Dense (BGE / Legal-Embed / SAILER) | 0.2–8.0% | — | 0.0–4.3% | — |
| Hybrid RRF | 8.3% | 9.5% | 10.1% | 15.3% |
| BM25 + recursive-512 | 11.5% | 12.9% | 17.2% | 19.8% |
| + cross-encoder rerank | 10.0% | 10.5% | 13.8% | 14.6% |
| **Qwen3-Embedding-0.6B + recursive-512** | **12.6%** | **15.2%** | — | — |
| BM25 bigram + recursive-512 | 10.6% | 12.6% | 20.1% | 27.1% |
| **BM25 5-gram (whole doc)** | — | — | **20.7%** | **39.9%** |

Qwen3 is the first dense model to beat BM25 on statute retrieval. PCR numbers
for Qwen3 pending. Test split: BM25 + recursive-512 gets 12.9% LSR / 17.9% PCR F1.

5-gram BM25 nearly reproduces the IL-PCSR paper's best lexical PCR row under
their best-k protocol: F1@2 32.2% vs. 33.3%, MAP 39.9% vs. 44.0%, MRR 57.3%
vs. 58.6%. The bigram variant does not reproduce their paragraph-level LSR
row (12.3% vs. 18.6% best-k F1).

## Tests

```bash
pytest tests/ -q
```

## Repository layout

```
.
├── src/legal_rag/       Core library (retrievers, chunkers, evaluator)
├── tests/               Unit and smoke tests
├── data/fixtures/       Local fixtures (committed)
├── data/raw/            Downloaded datasets (gitignored)
├── configs/             Experiment configurations
├── scripts/             download_il_pcsr.py, run_phase1.py
├── results/             Aggregated experiment outputs
└── report.tex           Paper draft
```
