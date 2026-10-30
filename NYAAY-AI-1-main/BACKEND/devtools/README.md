# BACKEND/devtools

This directory contains **development utilities, smoke tests, and integration verification scripts** used during the active development of NYAAY AI. These are **not part of the production application** and are not executed during normal server operation or CI.

## Contents

| File | Purpose |
|------|---------|
| `test_pipeline.py` | End-to-end smoke test: ingestion → ChromaDB → RAG retrieval pipeline |
| `verify_upload_e2e.py` | E2E verification of the Upload Chat service (document upload + query + persistence) |
| `verify_kanoon_e2e.py` | E2E verification of the Know Your Kanoon query pipeline |
| `verify_deletion.py` | Verifies document and conversation deletion logic |
| `verify_models.py` | Checks Gemini model availability and response formats |
| `verify_summary_fallback.py` | Tests document summarisation fallback behaviour |
| `test_query.py` | Standalone query test against a running server |
| `test_orchestrator.py` | Direct orchestrator smoke test |
| `test_kanoon.py` | HTTP-level Kanoon endpoint test against a running server |
| `test_kanoon_mock.py` | Mock-based Kanoon endpoint test |
| `test_gemini_format.py` | Verifies Gemini API response format compatibility |
| `test_pydantic.py` | Validates Pydantic schema models |
| `test_sync.py` | Auth sync endpoint test (POST /api/auth/sync) |
| `inspect_db.py` | SQLite inspection utility for debugging database state |
| `find_working_model.py` | Checks which Gemini model names are currently available |
| `latency_profiler.py` | Measures per-endpoint response latency |
| `audit_tests.py` | Runs a quick audit of test coverage across routes |
| `generate_mock_corpus.py` | Generates a mock legal corpus for local development |
| `generate_templates.py` | Generates default legal document templates |

## Usage

Most scripts require the backend to be running locally (`uvicorn app.main:app --reload`) and a `.env` file to be configured. Run from the `BACKEND/` directory:

```bash
cd BACKEND
python devtools/test_pipeline.py
python devtools/verify_upload_e2e.py
```

> **Note:** These scripts are development aids. The production test suite lives in `BACKEND/tests/`.
