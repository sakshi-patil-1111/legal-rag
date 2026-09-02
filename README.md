# Legal RAG Project

Modular, reproducible experimental framework for evaluating retrieval and agentic RAG strategies on legal case analysis and decision support.

## Phase 0: Tiny Local Fixture

The project starts with a minimal end-to-end fixture that proves:

```text
Query -> Corpus -> Representation -> BM25 Retriever -> Results -> Evaluation
```

No external benchmarks are downloaded in this phase.

### Run the smoke test

```powershell
$env:PYTHONPATH="src"; python scripts/run_phase0.py
```

### Run unit tests

```powershell
$env:PYTHONPATH="src"; python -m unittest discover -s tests
```

## Phase 1: IL-PCSR Smoke Test

Run the statute and precedent retrieval smoke test against the local IL-PCSR fixture:

```powershell
$env:PYTHONPATH="src"; python scripts/run_phase1.py
```

## Phase 2: LegalBench-RAG Smoke Test

Run the external validation smoke test against the local LegalBench-RAG fixture:

```powershell
$env:PYTHONPATH="src"; python scripts/run_phase2.py
```

## Compare all strategies on the IL-PCSR fixture

Run a controlled grid over chunkers, retrievers, query strategies, and rerankers to see which combination scores best:

```powershell
$env:PYTHONPATH="src"; python scripts/compare_grid.py
```

It writes `results/comparison_grid.csv` (one row per run) and `results/comparison_grid_summary.json` (best per task).

## Repository layout

```
.
├── src/legal_rag/       Core library
├── tests/               Unit and smoke tests
├── data/fixtures/       Local fixtures
├── configs/             Experiment configurations
├── scripts/             Executable experiment scripts
└── results/             Saved experiment outputs
```
