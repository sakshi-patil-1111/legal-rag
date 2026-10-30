# Legal RAG Project

Reproducible experimental framework for comparing retrieval strategies on legal
case analysis. Currently focused on the IL-PCSR benchmark (Indian statute and
precedent retrieval). See `PLAN.md` for the project handoff doc and
`BTech_Latex_Report/thesis.tex` for the dissertation.

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

## Agentic demo

`LegalAgent` (`src/legal_rag/legal_agent.py`) runs a bounded
route → retrieve → reflect → synthesise loop: an LLM plans per-corpus
queries (statute / precedent), retrievers act as tools, a reflection step
can issue refined queries, and the final JSON dossier's citations are
validated against the retrieved set (unverifiable ids are dropped and
recorded as warnings).

```bash
python scripts/agent_demo.py --case "<case description>" --legs bm25
```

The demo builds the BM25 leg locally (index is cached in `data/indexes/`),
prints the dossier, evidence list, and step-by-step trace. It runs fully
offline except LLM calls — without a key it still exercises routing through
retrieval via a deterministic fallback.

LLM config (any OpenAI-compatible endpoint or Gemini REST; plain `urllib`,
no vendor SDK):

| Env var | Purpose |
|---------|---------|
| `LLM_PROVIDER` | `gemini` (default) or `openai` |
| `GEMINI_API_KEY` | key for the Gemini provider |
| `LLM_API_KEY` | key for OpenAI-compatible providers |
| `LLM_BASE_URL` | override endpoint (e.g. local vLLM/Ollama) |
| `LLM_MODEL` | model name (default `gemini-3.8-flash`) |

## Headline results (dev split, 627 queries)

| Method | LSR F1@10 | LSR MAP | LSR MRR | PCR F1@10 | PCR MAP | PCR MRR |
|--------|-----------|---------|---------|-----------|---------|---------|
| BM25 whole-doc unigram | 8.4% | 9.6% | 20.5% | 11.0% | 18.4% | 30.8% |
| BM25 + recursive-512 | 11.5% | 12.9% | 29.4% | 17.2% | 19.8% | 33.0% |
| BM25 2-gram + rec-512 | 10.6% | 12.6% | 30.8% | 20.1% | 27.1% | 43.7% |
| **BM25 5-gram (whole doc)** | — | — | — | **20.7%** (32.2%@2) | **39.9%** | **57.3%** |
| Dense (BGE / Legal-Embed / SAILER) | 0.2–8.0% | — | — | 0.0–4.3% | — | — |
| Qwen3-Embedding-0.6B | 12.6% | 15.2% | 30.9% | 11.1% | 17.2% | 27.2% |
| Qwen3-Embedding-4B | 14.3% | **19.8%** | 37.4% | 12.6% | 19.6% | 29.9% |
| Hybrid RRF (5-gram + Qwen3-0.6B) | 13.7% | 17.9% | 38.8% | 19.2% | 30.0% | 45.1% |
| Hybrid RRF (5-gram + Qwen3-4B) | 14.7% | 19.1% | 40.5% | 19.7% | 31.6% | 46.4% |
| + bge-reranker-v2-m3 CE rerank | 7.5% | 6.6% | 16.1% | 6.9% | 6.5% | 13.7% |
| **+ gpt-6-luna listwise rerank** | **14.8%** (23.8%@2) | **25.2%** | **50.9%** | 16.6% | 25.5% | 39.2% |

Key findings:

- **5-gram BM25 nearly reproduces the paper's best lexical PCR row** under
  their best-k protocol: F1@2 32.2% vs. 33.3%, MAP 39.9% vs. 44.0%, MRR
  57.3% vs. 58.6%. Independently reproduced on Kaggle CPU (20.8/40.0/57.4).
- **gpt-6-luna listwise rerank lifts LSR over every non-fine-tuned paper
  row**: MAP 25.2% vs. para-wise BM25's 21.8%; MRR 50.9% vs. 44.3%.
  It mildly hurts PCR — LLM reranking is task-asymmetric.
- **Fusion dilution**: RRF helps LSR but hurts PCR because the dense leg
  is too weak to partner with 5-gram BM25 (best-k F1 24.4% vs. 32.2%
  alone). Fusion only helps when both legs are comparable.
- **Truncated cross-encoders destroy recall**: reranking 4.5K-token
  queries at 2K tokens drops PCR R@10 from ~53% to 19% — the model
  judges on the query's opening section only.
- **PRF does not help** on this benchmark (ΔMAP ≈ 0 on both filtered and
  full 16.8M-shingle indexes); **rhetorical-role filtering alone fails**
  (~4-6 F1) but dropping Court Reasoning text is free for PCR and helps
  LSR slightly. See `results/cpu_*` and `PLAN.md`.

Test split: BM25 + recursive-512 gets 12.9% LSR / 17.9% PCR F1.

In flight on Kaggle T4: contrastive fine-tune of Qwen3-0.6B on the
5,017-query train split (`scripts/finetune_embedder.py`) and a BGE-M3
dense+sparse+ColBERT-MaxSim evaluation (`scripts/run_bgem3.py`) — kernel
dirs in `kaggle/`. See `PLAN.md` for the full experiment ladder, paper-vs-
ours protocol notes, and thesis roadmap.

## Tests

```bash
pytest tests/ -q
```

## Repository layout

```
.
├── src/legal_rag/       Core library (retrievers, chunkers, evaluator,
│                        legal_agent, llm, factory, reranker)
├── tests/               Unit and smoke tests (30)
├── data/fixtures/       Local fixtures (committed)
├── data/raw/            Downloaded datasets (gitignored)
├── configs/             Experiment configurations
├── scripts/             run_phase1.py, run_cpu_experiments.py,
│                        finetune_embedder.py, run_bgem3.py,
│                        analyze_results.py, download_il_pcsr.py,
│                        agent_demo.py
├── kaggle/              Kernel definitions (cpu/gpu results runs)
├── modal_app.py         Modal app: data bootstrap + GPU experiment runs
├── analysis/            Bootstrap CIs + pgfplots figures (*.tex, *.json)
├── results/             Aggregated experiment outputs (summaries committed)
├── BTech_Latex_Report/  thesis.tex (compiles via tectonic)
├── PLAN.md              Handoff doc: experiment ladder, thesis roadmap
└── report.tex           Early paper draft (superseded by thesis)
```
