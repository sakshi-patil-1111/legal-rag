# Legal RAG Project

Modular, reproducible experimental framework for evaluating retrieval and agentic RAG strategies on legal case analysis and decision support.

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

# LegalBench-RAG (open)
# Download from Dropbox and unzip into data/raw/legalbench_rag/
# See: https://github.com/ZeroEntropy-AI/legalbenchrag
```

## Running

```bash
# Phase 0: tiny fixture smoke test
python scripts/run_phase0.py

# Phase 1: IL-PCSR
python scripts/run_phase1.py                      # fixture
python scripts/run_phase1.py phase1_il_pcsr.json  # real data

# Phase 2: LegalBench-RAG
python scripts/run_phase2.py                                      # fixture
python scripts/run_phase2.py phase2_legalbench_rag_privacy_qa.json # privacy_qa subset
python scripts/run_phase2.py phase2_legalbench_rag.json            # full

# Tests
pytest tests/ -q
```

## Repository layout

```
.
├── src/legal_rag/       Core library
├── tests/               Unit and smoke tests
├── data/fixtures/       Local fixtures (committed)
├── data/raw/            Downloaded datasets (gitignored)
├── configs/             Experiment configurations
├── scripts/             Executable experiment scripts
├── results/             Saved experiment outputs
└── AGENTS.md            Project plan and status
```
