# PLAN.md — Handoff Document

Working plan and handover guide for the legal-RAG research project.
Read this first. It covers what is done, what is running, what to try
next (in priority order), what not to bother with, how to finish the
B.Tech report, and how everything is wired.

- Repo: `legal-rag`, working branch `neel` (now also pushed to `main`).
- Paper under study: **IL-PCSR** (EMNLP 2025 Findings), source in
  `arXiv-2511.00268v1/`. Main results table: `sections/experiments.tex`.
- Thesis draft: `BTech_Latex_Report/thesis.tex` (compiles clean, 42 pp).
- Agent architecture being adapted: `NYAAY-AI-1-main/` (hackathon project,
  now tracked in the repo — will be modified and integrated for the
  dissertation; see §5).

---

## 1. Where things stand (as of last update)

### 1.1 Result ledger — dev split, 627 queries, %

Protocol caveat: **the paper reports best-k macro-F1 on the TEST split;
ours are F1@10 on DEV** (best-k in parentheses where it differs).
Comparisons are approximate, never claim a clean win without matching
protocol.

| Method | LSR F1@10 | LSR MAP | LSR MRR | PCR F1@10 | PCR MAP | PCR MRR |
|---|---|---|---|---|---|---|
| BM25 unigram whole-doc | 8.4 | 9.6 | 20.5 | 11.0 | 18.4 | 30.8 |
| BM25 2-gram + rec-512 | 10.6 | 12.6 | 30.8 | 20.1 | 27.1 | 43.7 |
| **BM25 5-gram whole-doc** | — | — | — | **20.7 (32.2@2)** | **39.9** | **57.3** |
| Qwen3-Emb-0.6B dense | 12.6 | 15.2 | 30.9 | 11.1 | 17.2 | 27.2 |
| Qwen3-Emb-4B dense | 14.3 | **19.8** | 37.4 | 12.6 | 19.6 | 29.9 |
| Hybrid RRF 5-gram + Qwen3-0.6B (c2) | 13.7 | 17.9 | 38.8 | 19.2 | 30.0 | 45.1 |
| Hybrid RRF 5-gram + Qwen3-4B (c3) | 14.7 | 19.1 | 40.5 | 19.7 | 31.6 | 46.4 |
| d2: bge-reranker-v2-m3 CE over c2 top-50 | 7.5 | 6.6 | 16.1 | 6.9 | 6.5 | 13.7 |
| **d3: gpt-6-luna listwise over c2 top-50** | **14.8 (23.8@2)** | **25.2** | **50.9** | 16.6 | 25.5 | 39.2 |
| SAILER / BGE / Legal-Embed dense | 0.2–8.0 | — | — | 0.0–4.3 | — | — |

### 1.2 Paper rows to aim at (test, best-k F1)

| Row | LSR F1 / MAP / MRR | PCR F1 / MAP / MRR |
|---|---|---|
| Best lexical (5-gram BM25) | 16.98 / 17.88 / 40.08 | **33.29 / 43.98 / 58.55** |
| Para-wise BM25 2-gram | 18.59 / 21.82 / 44.32 | 27.87 / 38.15 / 52.32 |
| SAILER fine-tuned (summaries) | 23.49 / 31.42 / 50.25 | 15.00 / 20.43 / 27.72 |
| Para-GNN + BM25 (transfer) | 39.44 / 52.13 / 73.77 | 38.77 / 50.21 / 63.81 |
| GPT-4.1 rerank stage-2 | 46.11 / 61.06 / 81.55 | 43.31 / 54.43 / 68.88 |

### 1.3 Established findings (all verified, some twice)

1. **PCR is a lexical task; LSR is semantic.** 5-gram BM25 is the PCR
   champion (ties paper: 32.2 vs 33.29 best-k F1). Every dense leg
   *dilutes* PCR under RRF — fusion only helps when legs are comparable.
2. **LLM listwise rerank strongly helps LSR** (+7.3 MAP, +12.1 MRR over
   the c2 hybrid) and mildly hurts PCR. Asymmetry is real and consistent.
3. **Truncated cross-encoder reranking actively destroys recall**
   (d2: R@10 19.2 vs 53 for its base pool). On 4.5K-token queries the CE
   scores on the opening section only → anti-correlated ordering.
   Second data point: ms-marco-MiniLM CE also hurt (13.8 vs 17.2).
4. **PRF does not help here.** Verified on both the filtered (df=2) and
   the full 16.8M-shingle index: ΔMAP ≈ 0. Legal queries are already
   long and redundant; expansion adds noise. Do not retry naive PRF.
5. **Rhetorical roles:** no single section (Facts/Issue) can retrieve
   alone — collapse to ~4-6 F1 on both tasks. Dropping "Court Reasoning"
   is free on PCR and *helps* LSR (+0.4 F1, +0.7 MAP, +1.2 MRR) —
   reasoning prose is topical noise for statute matching. First
   rhetorical-role ablation on IL-PCSR; write it up.
6. **Reproducibility:** unfiltered 5-gram index rebuilt independently on
   Kaggle CPU → 20.8/40.0/57.4 vs original 20.7/39.9/57.3. Modal c2 vs
   Kaggle c2: within ~0.4 MAP.

### 1.4 In flight

| Job | Where | What | Status check |
|---|---|---|---|
| `legal-rag-qwen3-ft` | Kaggle T4 | Contrastive FT of Qwen3-0.6B on 5,017 train pairs → dev eval | `kaggle kernels status` / email |
| `legal-rag-bgem3` | Kaggle T4 | BGE-M3 dense+sparse+RRF+ColBERT MaxSim rerank | same |

Modal work is all complete (b2b/c2/b3/c3/d2/d3 results in `results/`).

---

## 2. Experiment ladder — priorities

Ordered by expected value ÷ effort. Legend: **P0** = running now,
**P1** = do next, **P2** = good if time, **X** = do not bother (disproved
or low value).

### P0 — in flight, just collect results

- [ ] **Qwen3-0.6B contrastive fine-tune** (`scripts/finetune_embedder.py`)
  66,753 pairs from train split, MNRL loss, 1 epoch, batch 4×2048,
  Adafactor, grad-checkpointing. Output: `ft_out/ft_{task}_summary.json`
  + saved model. *This is the biggest lever* — the paper's own fine-tunes
  gave +200-300% on LSR; ours is a modern 0.6B base.
- [ ] **BGE-M3 all-modes** (`scripts/run_bgem3.py`) — dense, learned
  sparse, RRF union, ColBERT MaxSim over union pool (top 50+50 → 10).
  The late-interaction family the paper skipped entirely. Watch for the
  PCR number — token-level matching should respect lexical precision.

### P1 — next, high value

- [ ] **LLM rerank over a strong base.** d3 ran over the weak c2 pool
  (0.6B leg). Rerun `stage_d3_hybrid_llm_rerank.json` with retrieval
  swapped to the c3 config (4B leg) or the fine-tuned model — better
  pool → higher rerank ceiling. Est. cost < $1 (same 1,254 listwise
  calls × ~3K tok). Also try `doc_chars` 1000→2000 in `LLMReranker`.
- [ ] **Fine-tuned model retrieval run.** Once qwen3-ft finishes, plug
  `results/ft_qwen3/model` (or the downloaded `ft_out/model`) into a
  `stage_b*` config (`dense_model_name` = local path) and re-run
  `run_phase1.py` — then re-run d3 on that pool. This is the composite:
  `5-gram BM25 + FT dense → RRF → gpt-6-luna`.
- [ ] **Learning-to-rank fusion** (replaces naive RRF). Features per
  candidate: BM25 score, dense score, RRF rank, per-leg rank, n-gram
  coverage, doc length, rhetorical-role flags. LightGBM LambdaMART on
  train split, eval on dev. ~2h of feature plumbing; probably +2-4 F1
  over RRF and directly attacks the fusion-dilution finding.
- [ ] **Cross-task conditioned retrieval** (novel, motivated by the
  paper's own stage-2 result). Two variants:
  (a) protocol-fair: retrieve statutes first, append top statute
  titles/text to the precedent query (and vice versa);
  (b) upper-bound: inject gold relevant IDs like the paper's stage-2.
  Implement as a `query` strategy in `src/legal_rag/query.py`.
- [ ] **d3-style rerank applied to PCR with a lexical-aware prompt.**
  The gpt-6-luna rerank hurt PCR — hypothesis: the generic "relevance"
  prompt ignores the citation-precedent signal (shared statutes, similar
  issues). Try a PCR-specific prompt mentioning "cited as precedent for
  similar legal issues". Cheap edit in `reranker.py` `LLMReranker.prompt`.

### P2 — worthwhile if time remains

- [ ] **Agentic loop benchmark.** `LegalAgent` already does
  route→retrieve→reflect→synthesise. Add a benchmark harness: run the
  agent on dev queries, count retrieval steps, measure F1 of the agent's
  final ranked union vs single-shot retrieval, plus citation-verification
  rate. Nobody has benchmarked an agentic loop on IL-PCSR — a modest F1
  with an auditable trace is still a systems contribution.
- [ ] **Role-aware feature fusion** (not filtering — that failed).
  Keep full-doc retrieval but add role-segment scores as LTR features,
  or build per-role sub-queries and fuse rankings. Honours finding 1.3-5.
- [ ] **SPLADE** (`naver/splade-cocondenser-ensembledistil`) — learned
  sparse expansion; bridges lexical/dense. One model, moderate plumbing.
- [ ] **Better PRF** — expand with unigram terms from top docs weighted
  by RM3 rather than raw shingles, and weight expansion terms down.
  Low priority: naive PRF failed; only revisit if LTR needs query-side
  features.
- [ ] **Test-split run of the champion config** for the thesis's final
  table (only once, at the end — see §4.4 protocol).

### X — measured, do not repeat

- ~~Naive PRF (shingle expansion)~~ — wash on both index sizes.
- ~~Hard rhetorical-role query filtering~~ — collapses to ~4-6 F1.
- ~~Truncated-CE rerank~~ — destroys recall at 2K max_length on 4.5K
  queries. If revisiting CEs, aggregate per-chunk scores to doc level.
- ~~SAILER off-the-shelf~~ — 0.0-0.2 F1; needs fine-tuning to be useful,
  and Qwen3 is a strictly better base.
- ~~BM25 + BGE/Legal-Embed hybrid~~ — weak legs, superseded by Qwen3 legs.
- ~~Re-uploading 289 MB data to Modal~~ — bootstrap inside the container
  via `HF_TOKEN` secret (already implemented in `modal_app.py`).

---

## 3. LLM reranking — paper vs ours, and how to extend

| | Paper (IL-PCSR §experiments) | Ours (d3) |
|---|---|---|
| Model | GPT-4.1 | `gpt-6-luna`, reasoning_effort=medium |
| Input | stage-1: docs only; stage-2: docs + *other task's* top results | docs only (numbered 1000-char snippets) |
| Granularity | full document text | snippet + JSON rank order out |
| Pool | their own top-k retriever output | hybrid c2 top-50 → 10 |
| Result | LSR 46.11 / PCR 43.31 F1 | LSR MAP 25.2 / MRR 50.9 (over base 17.9/38.8) |
| Failure mode | — | PCR −4.5 MAP: generic relevance prompt ignores precedent signals |

Extension ideas (in `src/legal_rag/reranker.py` `LLMReranker`):

1. **Cross-task snippets** — replicate paper stage-2: pass top statute
   results into the PCR prompt context and vice versa. Straightforward:
   evaluate statute first, thread its output into the precedent rerank
   prompt. Highest-fidelity replication of their best row.
2. **Task-aware prompts** — for PCR mention "cited precedent for similar
   issues"; for LSR mention "statutory provisions governing these facts".
3. **Longer snippets** — `doc_chars` 1000→2000-3000 for precedents
   (long docs need more than the head section). Watch token budget:
   20 docs × 3000 chars ≈ 20K tok/call ≈ still ~$0.002-0.01 per call.
4. **Sliding-window doc scoring** — score each chunk, aggregate max/mean
   to doc score (fixes the "only sees head section" problem like d2's).
5. **Track usage** — `LLMReranker` already counts calls/failures; log
   token usage per call for the thesis cost table.

---

## 4. B.Tech report — how to finish it properly

`BTech_Latex_Report/thesis.tex` compiles clean (tectonic). It currently
has 7 chapters, TikZ diagrams, native pgfplots figures, bootstrap CIs.

### 4.1 Still missing / to strengthen

- [ ] **Placeholders**: registration number (line ~11), supervisor (line ~13).
- [ ] **Literature review depth**: currently cites IL-PCSR + a handful.
  Add ~10-15 more: legal IR (Lexis/CaseLaw surveys), dense retrieval
  (DPR, ANCE, ColBERT, SPLADE), domain adaptation (SAILER, CaseHOLD,
  legal-BERT family), legal RAG/agents (NYAAY-style systems, retrieval
  for legal QA), reranking (monoT5, RankGPT/listwise LLM rerankers),
  rhetorical-role literature (Bhattacharya, Ghosh, Kalamkar et al. —
  the IIT KGP rhetorical roles project this dataset derives from).
  `references.bib` is the file; source BibTeX from DBLP/S2.
- [ ] **Limitations section** (examiners look for it): dev-vs-test
  protocol gap, fixed-k vs best-k, no fine-tuned GNN baseline, single
  seed, snippet-vs-full-doc rerank, API-model drift, English-only,
  dataset-specific findings.
- [ ] **Figures to add**: (a) agentic-loop sequence diagram (TikZ or
  pgf-umlcd); (b) bar chart of "reranker effect" (c2 → d3 per metric);
  (c) per-role ablation bar chart; (d) F1-vs-k curves already emitted
  to `analysis/fig_*.tex` — ensure newest methods are included by
  re-running `scripts/analyze_results.py` after pulling finals.
- [ ] **Cost/latency table**: GPU-hours per experiment, OpenAI spend,
  Kaggle vs Modal hardware, index build times — required for honesty.
- [ ] **Reproducibility appendix**: exact commands, config names, seeds,
  kernel slugs, Modal app name, commit hash.
- [ ] **Abstract + conclusions rewrite** once final numbers land.

### 4.2 Presenting results like a research paper

- One **main table per task** (LSR, PCR) with our methods grouped:
  lexical / dense / hybrid / reranked / fine-tuned; paper rows in a
  separate block marked "test split, best-k". Never mix protocols in
  one column without a dagger/footnote.
- Report **F1@10 AND best-k F1** for every row (we already save all
  k's), plus MAP, MRR, R@10. Bootstrap 95% CIs on headline claims
  (`scripts/analyze_results.py` already computes them).
- **Ablation tables beat prose**: the roles ablation, PRF ablation,
  truncation-CE ablation are each a table + 1 paragraph.
- Claim framing: "matches" (Δ within CI), "exceeds" (non-overlapping
  CIs + same protocol), "approaches" (right direction, different
  protocol). Never "beats" across protocols.
- Negative results are contributions: PRF, role filtering, truncated
  CE — one short section "What did not work" is a credibility booster.

### 4.3 Diagram checklist

- [x] System architecture (TikZ, in thesis)
- [x] Agent loop (TikZ)
- [ ] Retrieval→rerank pipeline detail (per-stage pool sizes: 53,730
  chunks → top-50 → top-10)
- [ ] NYAAY-mapped component diagram (retriever/planner/verifier boxes
  labelled with our class names)

### 4.4 Protocol discipline for the final table

- Keep dev as the model-selection split; run the **test split exactly
  once** for the final champion config, report it as the headline
  comparable number. The paper's rows are test best-k — matching that
  is the only way to a clean claim.
- Record `git_commit` + config hash (the runner already stores both).

---

## 5. NYAAY-AI — first-class component, to be modified for the dissertation

`NYAAY-AI-1-main/` is a legal-assistance hackathon codebase (Flask app,
crew/agent-style orchestration, Indian-law focus) that is **now tracked
in this repository** — it will be modified and integrated as the
dissertation's agentic layer, not merely cited. Generated artifacts are
excluded via `NYAAY-AI-1-main/.gitignore` (chroma backup, uploads, audit
dumps); all source/docs/corpus/data are committed.

Layout worth knowing:

| Path | What it is |
|---|---|
| `BACKEND/app/` | Flask app + core modules (incl. `core/key_rotator.py`) |
| `BACKEND/corpus/` | Indian legal corpus it retrieves over (~10MB) |
| `BACKEND/data/` | knowledge/case data (~21MB) |
| `BACKEND/eval/`, `tests/` | their own eval + test harness |
| `FRONTEND/` | Vercel-deployed UI (~1.4MB) |
| `benchmark_*.json`, `benchmark_rrf*.py` | their retrieval benchmarks |

Integration direction (aligns with §2 P2 agentic work): port their
orchestration ideas onto `legal_agent.py`/`LegalAgent` and swap their
corpus/retrievers for our IL-PCSR retrievers, so the dissertation's
agent is benchmarkable on a standard dataset — NYAAY-AI alone has no
comparable evaluation.

Mapping already implemented in `src/legal_rag/legal_agent.py`:

| NYAAY concept | Our analogue | File |
|---|---|---|
| Task routing / crew roles | `LegalAgent` route step | `legal_agent.py` |
| Corpus tools | BM25 / dense / hybrid retrievers | `retrievers/` |
| Reflection / refinement | reflect step re-issuing queries | `legal_agent.py` |
| Answer synthesis w/ citations | JSON dossier + citation validation | `legal_agent.py` |
| Audit trail | step-by-step trace in dossier | `legal_agent.py` |

What to build for the thesis (priority order):

1. **Benchmarked agentic loop** (see P2): run agent on dev queries,
   compare final union-ranking F1 vs single-shot. Metrics: task-F1,
   retrieval calls/query, citation-validity rate, latency, $/query.
2. **Citation verifier** — already partially there (unverifiable ids
   dropped + recorded as warnings); add a numeric "groundedness" score
   to the dossier.
3. **Multi-leg fan-out** — agent issues statute AND precedent legs
   concurrently, merges via RRF; measure whether agent-chosen legs beat
   fixed pipelines.
4. **Bounded loop ablation** — 0/1/2 reflection rounds; shows whether
   reflection helps or just costs tokens.
5. Write up as "agentic retrieval evaluation" — the thesis chapter is
   already sketched; needs real numbers from item 1.

Do NOT: run its Flask app against IL-PCSR as a "baseline" (different
corpus/task, not comparable), or commit regenerated chroma backups /
uploads — but DO mine its orchestration, citation-verification, and
agent-role code for the dissertation's agentic layer.

---

## 6. Infrastructure cheat-sheet

| Piece | Where | Notes |
|---|---|---|
| HF dataset | `Exploration-Lab/IL-PCSR` (gated) | needs `HF_TOKEN`; bootstrap via `scripts/download_il_pcsr.py` |
| Kaggle dataset | `samudraneel05/il-pcsr-data` | queries/statutes/precedents.json at root |
| Kaggle kernels | `kaggle/<name>/` dirs | `kaggle kernels push` from each dir; kernels mount the dataset + clone branch `neel` |
| Kernel outputs | `kaggle kernels output <slug> -p <dir>` | per-query JSONs ~40MB each; use a re-export kernel (`kaggle/cpu-results/`) to skip giant caches |
| Modal | app `legal-rag-experiments` (deployed) | volumes: `legal-rag-data`, `legal-rag-results`, `legal-rag-hf`; secrets: `legal-rag-hf`, `legal-rag-openai` |
| OpenAI | `OPENAI_API_KEY` in `.env` (gitignored) | model `gpt-6-luna`, reasoning_effort=medium; ~$5 budget — one d3 run ≈ $0.5-1 |
| Mac safety | 8GB RAM | never build unfiltered n-gram index locally; use `min_df>=2` or Kaggle; `nice` the job |
| Tests | `pytest tests/ -q` → 30 tests | run before every commit |

**Security**: an OpenAI key and Modal token were once pasted in chat —
treat as compromised; rotate before submission, never commit `.env`.

### Common commands

```bash
# data
python scripts/download_il_pcsr.py                 # HF -> data/raw/il_pcsr

# experiments (config-driven)
python scripts/run_phase1.py configs/stage_a_ngram5.json

# CPU experiments (memory-safe, cached index)
python scripts/run_cpu_experiments.py --experiment base --task precedent \
    --ngram 5 --min-df 2
python scripts/run_cpu_experiments.py --experiment roles --task statute \
    --ngram 2 --min-df 2 --roles no_reasoning

# analysis (CIs, k-curves, length buckets -> analysis/*.tex + json)
python scripts/analyze_results.py

# Modal
modal run modal_app.py::bootstrap_data   # one-time data load into volume
modal run modal_app.py::run_experiment --config configs/stage_c3_hybrid_ngram_qwen3_4b.json
modal volume ls legal-rag-results stage_d3
modal volume get legal-rag-results stage_d3 results/stage_d3 --force

# Kaggle
kaggle kernels push -p kaggle/qwen3-ft
kaggle kernels status samudraneel05/legal-rag-qwen3-ft
kaggle kernels output samudraneel05/legal-rag-qwen3-ft -p /tmp/ft

# thesis
cd BTech_Latex_Report && tectonic thesis.tex    # or latexmk -pdf
```

---

## 7. Known quirks / traps for the next person

1. `.env` values may be single-quoted — strip quotes when passing to
   Modal secrets (`python-dotenv` strips them; `grep | cut` does not).
2. `modal run` ties remote work to the local client — use **deployed**
   functions (`.spawn()`) for anything long. Ephemeral runs die with
   your terminal.
3. Kaggle dataset mount path is `/kaggle/input/datasets/<slug>/`, not
   `/kaggle/input/<slug>/` — the kernel scripts glob `/kaggle/input/**`
   to be safe.
4. Kaggle kernel output includes the *entire* working dir — keep index
   caches OUT of the repo clone dir or output downloads become GBs
   (see `data/cache_cpu/`; scripts cache there — future kernels should
   redirect cache dirs to `/kaggle/tmp/`).
5. Errored-kernel logs: `kaggle kernels output` downloads the repo
   first; the `<slug>.log` lands at the end — be patient or grep the
   download dir.
6. `evaluate_query` expects `(doc_id, score)` tuples, not bare ids.
7. `RecursiveChunker.chunk()` takes `LegalDocument` objects, not raw
   strings — use `load_il_pcsr()`.
8. T4 has no bf16 — use fp16. `model_kwargs={"dtype": "float16"}` (new
   transformers) not `torch_dtype`.
9. Reasoning models (gpt-6-luna etc.) reject `temperature`; use
   `reasoning_effort` + `max_completion_tokens` — already handled in
   `llm.py`.
10. Per-query `*_statute.json`/`*_precedent.json` are gitignored by
    design (40MB each) — commit summaries only.
11. The results-volume dirs nest one level (`results/stage_d3/stage_d3/…`)
    after `modal volume get` — cosmetic.

---

## 8. Definition of done for the dissertation

- [ ] qwen3-ft + bgem3 results pulled, tables updated, CIs regenerated
- [ ] P1 items 1-3 run (rerank-over-strong-base, FT-model retrieval, LTR)
- [ ] One clean test-split number for the champion config
- [ ] Agentic loop benchmarked (even small — 100 queries is fine)
- [ ] Thesis: lit review ≥25 refs, limitations section, cost table,
      all diagrams, placeholders filled, abstract rewritten last
- [ ] README tables final, PLAN.md updated, secrets rotated
- [ ] `pytest` green, thesis compiles with no errors
