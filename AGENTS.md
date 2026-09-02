# Legal RAG — Master Project Plan and Status

## Project Identity

**Title:** Design of an Agentic RAG Framework for Automated Legal Case Analysis and Decision Support

**Type:** Student research project, targeting a publishable paper if results are novel and reproducible.

**Primary research question:**

> How do different design choices in a legal RAG pipeline affect retrieval quality and downstream legal decision support?

**Design choices under investigation:**

- document representation and parsing
- whole-document vs chunk-level retrieval
- chunking strategy
- lexical retrieval (BM25)
- dense/vector retrieval
- hybrid retrieval
- query rewriting
- HyDE
- query decomposition
- multi-query retrieval
- reranking
- iterative retrieval
- agentic/adaptive retrieval control

**Principles:**

- experimental rigor over feature count
- reproducibility
- modularity
- clean ablation studies
- fair comparisons
- resource efficiency
- meaningful research questions
- careful scope control

**Philosophy:**

```text
Build one reliable experimental pipeline
        ↓
Test many controlled ideas on one carefully chosen benchmark
        ↓
Identify strong configurations
        ↓
Freeze or shortlist the best configurations
        ↓
Validate only those configurations on additional benchmarks
        ↓
Gradually move toward agentic legal case analysis
```

Do NOT build a benchmark zoo. Do NOT run full Cartesian products.

---

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
- **LegalBench-RAG**: download from Dropbox, unzip into `data/raw/legalbench_rag/` (see https://github.com/ZeroEntropy-AI/legalbenchrag)

Fixtures for engineering tests live in `data/fixtures/`.

---

## Benchmark Phases

### Phase 0: Tiny Local Fixture — DONE

Engineering validation of the full pipeline on synthetic data.

Verifies: Load → Parse → Represent → Index → Retrieve → Rank → Evaluate → Save Results.

- 4 synthetic documents, 3 queries, BM25 only
- 25 unit tests passing
- Smoke test runs end-to-end

### Phase 1: Primary Development Benchmark — IL-PCSR — IN PROGRESS

Indian Legal corpus for Prior Case and Statute Retrieval.

Highly aligned with this project: retrieves both relevant statutes AND relevant precedents for the same legal situation.

```text
Legal Case / Legal Situation
            │
            ▼
      Retrieval System
       ┌────┴────┐
       ▼         ▼
   Statutes   Prior Cases
       │         │
       └────┬────┘
            ▼
      Legal Evidence
            │
            ▼
     Analysis / Support
```

**Two separate but related tasks:**

- Task A: legal situation → retrieve applicable statutes
- Task B: legal situation → retrieve relevant prior cases

Do NOT assume the best pipeline for statute retrieval is the best for precedent retrieval. This difference may itself become an important experimental result.

**Dataset:**
- 5,017 train / 627 dev / 627 test queries
- 936 statute candidates
- 3,183 precedent candidates
- Data downloaded from HuggingFace (Exploration-Lab/IL-PCSR, gated)
- Adapter works, reads real JSON correctly
- BM25 baseline ready

**What is set up:**
- Data download script (`scripts/download_il_pcsr.py`)
- Adapter (`src/legal_rag/datasets/il_pcsr.py`)
- BM25 retriever (hand-rolled, works)
- Chunkers: WholeDocument, FixedToken, FixedChar, Recursive (all with char offsets)
- Document-level metrics: recall@k, MRR
- Config-driven experiment scripts
- Real data config (`configs/phase1_il_pcsr.json`)

**Not yet set up (infrastructure gaps):**
- ~~Real sentence-transformer dense retriever~~ — DONE (BAAI/bge-base-en-v1.5 with disk cache)
- ~~LLM-based query rewriting and HyDE~~ — DONE (Gemini free tier via LLMProvider)
- ~~Cross-encoder reranker~~ — DONE (cross-encoder/ms-marco-MiniLM-L-6-v2)
- ~~NDCG and Precision@k~~ — DONE
- ~~Index persistence and caching~~ — DONE (embedding cache to data/cache/)
- ~~Reproducibility metadata~~ — DONE (experiment ID, timestamp, git commit, seed, config hash)
- ~~Dev/test split discipline~~ — DONE (configs default to dev split)
- ~~Staged ablation scripts~~ — DONE (run_stage.py + stage_a configs)
- Stratified development subset for expensive LLM experiments
- Cost/token tracking populated from LLM responses
- Result storage restructure (per-experiment dirs, JSONL traces)

### Phase 2: External Retrieval Validation — LegalBench-RAG — IN PROGRESS

US legal contract retrieval benchmark. Used to validate whether IL-PCSR conclusions transfer to a different legal domain.

```text
IL-PCSR:
Test many controlled configurations
        ↓
Shortlist best configurations
        ↓
LegalBench-RAG:
Test only shortlisted configurations
```

Research question: **Which retrieval design choices appear robust across legal domains, and which are jurisdiction-specific?**

**Dataset:**
- 6,889 queries across 4 sub-benchmarks (contractnli: 977, cuad: 4,042, maud: 1,676, privacy_qa: 194)
- 714 corpus documents, 79M characters
- Snippet-level ground truth: each query has snippets with (file_path, char_span, answer)
- Data downloaded from Dropbox (open, no gating)
- Adapter preserves snippet-level GT
- Dual eval mode: document-level (file match) + snippet-level (span overlap)

**What is set up:**
- Adapter with snippet preservation (`src/legal_rag/datasets/legalbench_rag.py`)
- Snippet-level metrics: recall@k, precision@k with char span overlap
- Chunk-level search in all retrievers (`search_chunks()`)
- Dual eval mode in evaluator (document + snippet)
- Configs for full run and privacy_qa subset

**Not yet set up:**
- Same infrastructure gaps as Phase 1 (most now resolved)
- Stratified development subset for expensive experiments

### Phase 3: Indian Downstream Legal QA — AIBE — NOT STARTED

All India Bar Examination dataset. Tests whether retrieval improvements translate into better downstream QA.

Compare only a small number of systems:
- System 1: LLM without retrieval
- System 2: Strongest fixed RAG pipeline
- System 3: Strongest query-enhanced or reranked RAG pipeline
- System 4: Agentic/adaptive RAG pipeline (if implemented)

Primary evaluation: MCQ accuracy, latency, cost, retrieval trace quality.

### Phase 4: Optional Large-Scale Validation — BhashaBench-Legal — NOT STARTED

Only if Phase 1-3 stable and resources available. Broader validation, English vs Hindi analysis, larger-scale downstream evaluation. Use stratified development subset. Run only final shortlisted systems.

### Phase 5: Optional Advanced Decision-Support Evaluation — NOT STARTED

Only after core project is mature. Possible: IL-TUR decision-oriented tasks, NyayaRAG-style evaluation. NOT a requirement for the core project.

---

## Architecture

```text
Dataset / Corpus
       │
       ▼
Document Preparation
       │
       ▼
Parser / Document Representation
       │
       ▼
Whole Document or Chunking Strategy
       │
       ▼
Index Construction
       │
       ▼
Query Strategy
       │
       ▼
Retriever
       │
       ▼
Optional Reranker
       │
       ▼
Evidence Aggregation
       │
       ▼
Optional Generator / Analyzer
       │
       ▼
Evaluation
       │
       ▼
Experiment Results
```

Each component is replaceable via abstract base classes:
- `Chunker` (chunking.py) — WholeDocument, FixedToken, FixedChar, Recursive
- `Retriever` (retrievers/base.py) — supports `search()` (doc-level, deduped) and `search_chunks()` (chunk-level, raw)
- `QueryStrategy` (query.py) — Direct, KeywordExpansion, HyDE (stub)
- `Reranker` (reranker.py) — NoOp, TokenOverlap

**Canonical schemas (Part 4):**
- `LegalQuery`: qid, text, task_type, benchmark, language, metadata, ground_truth
- `LegalDocument`: doc_id, doc_type, title, raw_text, source, metadata
- `LegalChunk`: chunk_id, parent_doc_id, text, position, chunking_metadata (incl. char_start/char_end), structural_metadata

Preserve original benchmark IDs. Never silently mutate benchmark ground truth.

---

## Whole-Document vs Chunk-Level Retrieval (Part 5)

This is an important early experimental question. Do NOT assume chunking is automatically beneficial. Legal documents often contain long-range context.

Phase 1 should explicitly compare:
- Approach A: whole-document retrieval
- Approach B: chunk-level retrieval → map chunk back to parent document

Chunk-to-document mapping strategies:
- any retrieved relevant chunk counts as retrieving the parent document
- aggregate chunk scores to document scores
- maximum chunk score per document
- top-k chunk aggregation

Log this methodology clearly.

---

## Chunking Experiments (Part 7)

Implement incrementally. Do NOT perform massive hyperparameter searches.

**Baseline:** Fixed-size chunking. Test 256, 512, 1024.

**Recursive chunking:** Section → Paragraph → Sentence → Token boundary.

**Semantic chunking:** One or two configurations only. Do not make embedding-model optimization a separate project.

**Legal/document-aware chunking:** Only where source structure supports it.
- Statute → Chapter → Section → Subsection
- Judgment → Facts → Issues → Arguments → Reasoning → Decision

For every chunking experiment, report: number of chunks, average chunk length, chunk length distribution, indexing time, retrieval metrics.

---

## Retrieval Experiments (Part 8)

Baseline: BM25. Then dense. Then hybrid.

Use only one strong embedding model initially. Do NOT benchmark ten embedding models.

First major comparison: Best BM25 vs Best Dense vs Best Hybrid.

Hybrid: implement Reciprocal Rank Fusion (done) and optionally simple weighted fusion. Do NOT build a learned hybrid model yet.

Candidate counts configurable: top 10, 20, 50.

Use development set for parameter selection. Do NOT tune on the final test set.

---

## Query Strategy Experiments (Part 9)

Only after establishing a strong base retriever.

Compare: Direct vs Rewrite vs HyDE.

```text
HyDE:
Query
↓
Generate hypothetical legal answer/document
↓
Use generated representation to assist retrieval
```

Do NOT implement rewrite, HyDE, multi-query, decomposition, and agentic planning all at once.

Use a development subset for expensive experiments. Run only promising strategies on the full test set.

Store: original query, transformed query, hypothetical document if generated, retrieval latency, model/token cost.

---

## Reranking (Part 10)

After identifying strong chunking + retriever + query strategy, compare:

- No Reranking vs Cross-Encoder Reranking

Only consider LLM reranking after cross-encoder comparison is working.

Design: Retrieve Top N → Rerank → Return Top K.

Log: original rank, original score, reranked rank, reranking score, latency.

Evaluate whether reranking produces meaningful improvement relative to computational cost.

---

## Metrics (Part 11)

**Retrieval:** Recall@1, Recall@3, Recall@5, Recall@10, MRR, NDCG, Precision@k where meaningful.

**Snippet-level (LegalBench-RAG):** snippet_recall@k, snippet_precision@k with char span overlap.

**Downstream QA:** Accuracy and task-specific metrics.

**Cost tracking:** Latency, number of retrieval calls, number of reranking calls, LM calls, token usage, approximate API cost.

Cost and latency should NOT be afterthoughts. The final paper should discuss tradeoffs.

**Current status:** recall@k, MRR, snippet_recall@k, snippet_precision@k implemented. NDCG, Precision@k, cost/token tracking MISSING.

---

## Staged Ablation Methodology (Part 12)

Do NOT run full Cartesian products. This is mandatory.

- **Stage A:** Fix retrieval to BM25. Test whole-doc vs fixed chunking vs recursive chunking. Shortlist winners.
- **Stage B:** Fix strongest representation. Test BM25 vs dense vs hybrid. Shortlist winners.
- **Stage C:** Fix strongest retrieval. Test direct vs rewrite vs HyDE. Shortlist winners.
- **Stage D:** Fix strongest pipeline. Test no reranking vs cross-encoder. Optionally test LLM reranking.
- **Stage E:** Build constrained agentic controller using strongest components.

**Current status:** `compare_grid.py` does a full Cartesian product (forbidden). Must be replaced with staged ablation scripts.

---

## Agentic RAG (Part 13)

Do NOT begin with a broad autonomous agent. Start with a constrained retrieval controller.

**Actions:** Retrieve directly / Rewrite query and retrieve / Use HyDE and retrieve / Stop and return evidence.

```text
Query
  ↓
Initial Retrieval
  ↓
Evaluate Evidence Sufficiency
  │
  ├── Sufficient → Stop
  │
  └── Insufficient
           ↓
     Select Alternative Strategy
           ↓
        Retrieve Again
           ↓
         Stop
```

**Limits:** Max 2 retrieval rounds initially. No infinite loops.

**Logging:** current state, chosen action, reason, query used, retrieved evidence, stopping reason.

**Key experiment:** Best Fixed Retrieval Pipeline vs Constrained Adaptive Retrieval Agent. The agent must justify its complexity through measurable gains.

**Current status:** `ConstrainedAgent` exists but is not truly adaptive — it runs strategies in sequence rather than evaluating evidence sufficiency and selecting actions.

---

## Experiment Configuration and Reproducibility (Part 14)

All experiments are configuration-driven (JSON configs in `configs/`).

Every run should save: Experiment ID, Timestamp, Configuration, Dataset version, Model names, Random seed, Metrics, Latency, Cost, Environment info, Git commit.

Cache expensive deterministic stages: processed documents, chunks, embeddings, indexes, deterministic query transformations.

**Current status:** Configs exist, results saved. MISSING: experiment ID, timestamp, git commit, seed, model names, environment info, caching.

---

## Result Storage (Part 15)

```text
results/
├── raw/
│   └── experiment_id/
│       ├── config.yaml
│       ├── predictions.jsonl
│       ├── traces.jsonl
│       └── metrics.json
│
└── aggregated/
    ├── summary.csv
    ├── comparison_tables/
    └── figures/
```

For each query, preserve: Query ID, Original Query, Query Transformation, Retrieved Documents/Chunks, Ranks, Scores, Reranked Results, Ground Truth, Final Prediction, Latency, Cost.

Do NOT throw away intermediate retrieval traces. They may be essential for the paper.

**Current status:** Results saved as flat JSON in `results/`. MISSING: per-experiment subdirectories, JSONL traces, aggregated summary CSV, figures.

---

## Resource Constraints (Part 16)

1. Use tiny fixtures for engineering tests.
2. Use development subsets for expensive exploratory experiments.
3. Run full test sets only for shortlisted configurations.
4. Cache embeddings and indexes.
5. Avoid unnecessary LLM calls.
6. Use deterministic seeds where possible.
7. Prefer one strong baseline over many poorly controlled baselines.
8. Do not download or process huge external benchmarks until required.
9. Do not make expensive commercial APIs mandatory.
10. Support configurable model providers.

The project should remain useful with local embedding models, CPU or limited GPU, and optional external APIs.

---

## Testing (Part 17)

Every major component should have tests. Use small fixtures. Do NOT require downloading large datasets during unit tests.

**Minimum coverage:** dataset loading, schema validation, document representation, chunking boundaries, metadata preservation, retrieval interface consistency, hybrid fusion, reranking order, metric calculation, experiment configuration validation, result persistence, agent stopping conditions.

**Current status:** 25 tests passing covering schemas, chunking, retrievers, query, reranker, metrics, datasets, pipeline, agent. MISSING: NDCG test, snippet metrics test, config validation test, result persistence test.

---

## Workflow (Part 18)

Work phase by phase. For each phase:
1. Inspect existing code.
2. State the objective.
3. Identify the minimum implementation required.
4. Implement it.
5. Run tests.
6. Run a smoke test.
7. Fix failures.
8. Summarize completed work.
9. List remaining risks and assumptions.
10. Stop before the next major phase unless explicitly instructed to continue.

Do NOT silently invent dataset formats, credentials, API keys, benchmark splits, or ground-truth relevance labels.

If dataset access is blocked or gated: document the issue, create the adapter structure, use a local fixture for engineering, do NOT fabricate benchmark results.

---

## Infrastructure Gaps (Priority Order)

1. ~~NDCG + Precision@k metrics~~ — DONE
2. ~~Reproducibility metadata in results~~ — DONE
3. ~~Real sentence-transformer dense retriever~~ — DONE
4. ~~Index persistence and caching~~ — DONE
5. ~~Dev/test split discipline~~ — DONE
6. ~~Staged ablation scripts~~ — DONE (run_stage.py + stage_a configs)
7. ~~Cross-encoder reranker~~ — DONE
8. ~~LLM-based query rewriting + HyDE~~ — DONE (Gemini free tier)
9. **Result storage restructure** (per-experiment dirs, JSONL traces, aggregated CSV)
10. **Truly adaptive agent** (evaluate evidence sufficiency, select actions)
11. **Stratified dev subset** for expensive LLM-based experiments
12. **Cost/token tracking** populated from LLM responses into results

---

## Research Questions to Build Toward

- Does chunking help legal retrieval, or can it destroy useful long-range context?
- Are statutes and precedents best retrieved using the same strategy?
- When does hybrid retrieval outperform purely lexical or dense retrieval?
- Does HyDE improve legal retrieval enough to justify its cost?
- Does reranking consistently help?
- Can a constrained adaptive retrieval agent outperform the strongest fixed pipeline?
- Which conclusions transfer beyond the original Indian legal benchmark?
- Do better retrieval systems actually improve downstream legal question answering and decision support?

Build toward answering these rigorously. Prioritize rigorous science over feature count. Prioritize controlled baselines before advanced agentic behavior. Do not confuse complexity with research contribution.
