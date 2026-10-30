# NYAAY AI — RAG Changes Report (As-Built Engineering Reference)

> **Purpose.** A single, exhaustive record of every change made to the NYAAY AI legal-RAG system across three workstreams — (1) fixing the retrieval pipeline for correctness, (2) ingesting the Supreme Court judgment corpus, and (3) reducing end-to-end response time. Written to be the durable context document for anyone continuing this project. Nothing intentionally omitted.
>
> **Branch:** `rag-improvements-phase2-4` · **Base:** `main` · **Date of report:** 2026-08-27
> **Companion doc:** [`DOCS/RAG_IMPROVEMENT_PLAN.md`](RAG_IMPROVEMENT_PLAN.md) is the original design/spec (item labels A1–A5, B1–B10, Part C). This report is the *as-built* verification of that plan plus the work that went beyond it.

---

## Table of Contents

1. [Executive summary & headline metrics](#1-executive-summary--headline-metrics)
2. [System architecture recap](#2-system-architecture-recap)
3. [Invariants — the contract that must be preserved](#3-invariants--the-contract-that-must-be-preserved)
4. [Part A — Retrieval correctness fixes (A1–A5)](#4-part-a--retrieval-correctness-fixes-a1a5)
5. [Part B — Latency optimization (B1–B10)](#5-part-b--latency-optimization-b1b10)
6. [Supreme Court judgment ingestion](#6-supreme-court-judgment-ingestion)
7. [Statute/scheme corpus ingestion & structural chunking](#7-statutescheme-corpus-ingestion--structural-chunking)
8. [Generation path & quality gates](#8-generation-path--quality-gates)
9. [Frontend rendering changes](#9-frontend-rendering-changes)
10. [Configuration reference](#10-configuration-reference)
11. [Commit history mapping](#11-commit-history-mapping)
12. [Verification & benchmarking](#12-verification--benchmarking)
13. [Known discrepancies & future work](#13-known-discrepancies--future-work)
14. [Operational procedures (re-ingest, rebuild, run)](#14-operational-procedures-re-ingest-rebuild-run)

---

## 1. Executive summary & headline metrics

The RAG system was overhauled in three phases, all on branch `rag-improvements-phase2-4`:

- **Phase 1 — Retrieval correctness** (commit `29646e0`, merged into `main`): removed a scoring bug that starved the reranker, fixed a leaked metadata multiplier, and unified all scoring onto the cross-encoder's calibrated sigmoid score. This is the change with the largest *quality* impact.
- **Phase 2–4 — Latency + chunking + config** (commit `0b22bef`): overlapped the analysis LLM with provisional retrieval on the streaming path, fixed an off-by-one bug in statute section metadata (required re-ingest), and cleaned up config/dead code.
- **Latency finishing pass** (commit `3d95fcc`): the "rerank-once" multi-query fan-out, a 429/quota fallback across Gemini flash models, and a fix to the thinking-config that never actually took effect before.
- **Uncommitted at time of report** (staged in this session): `orchestrator.py` output-token bump (2048→8192) at two generation sites, and three frontend renderers hardened to parse the CIVIC JSON dossier. Plus this report and the plan doc.

### Verified corpus state (queried live from `chroma_db/chroma.sqlite3`)

| Collection | Purpose | Chunks | Source docs |
|---|---|---:|---:|
| `supreme_court_cases` | SC judgment chunks | **58,689** | **4,367** judgments ingested (2 failed of 4,369 source JSON files) |
| `nyaay_knowledge` | statutes + welfare schemes | **8,246** | **100** `.md`/`.txt` corpus files |

### Latency (single dev machine, CPU-only, measured during this work)

- **Before:** ~25.9 s end-to-end.
- **After:** ~12–13 s end-to-end (a ~2× improvement), with generation (~6.5 s of ~13 s) being the dominant remaining cost — it is bound by answer length (~1,650 output tokens at ~230 tok/s on the free-tier flash model), not by retrieval.
- **Final product decision:** keep full answer detail and accept ~12–13 s rather than trim answer richness for marginal latency. Retrieval was tuned as far as it could go without hurting recall (see [§12](#12-verification--benchmarking)).

> ⚠️ Latency numbers are from a loaded developer laptop and vary run-to-run due to CPU contention (the cross-encoder is CPU-bound). Retrieval *result sets* were proven byte-identical across runs, so observed latency swings were contention, not regression.

---

## 2. System architecture recap

**Pipeline stages (per query):**

```
query → structured analysis (LLM) → embedding → hybrid retrieval → prompt construction → generation (LLM) → validation/gate → citations
```

**Hybrid retrieval** = dense + sparse + fusion + rerank:

- **Dense:** ChromaDB cosine search over **two** collections — `nyaay_knowledge` and `supreme_court_cases`. `vector_store.search(..., search_sc=True)` queries both and re-sorts the union by ascending distance (so SC content participates even without an explicit SC fan-out).
- **Sparse:** `rank_bm25.BM25Okapi` over a tokenized corpus. The **global** BM25 index is built from `nyaay_knowledge` **plus the entire** `supreme_court_cases` collection, which is why SC judgments are reachable through the ordinary BM25 path.
- **Fusion:** Reciprocal Rank Fusion (RRF, constant `k=60`) with a small metadata multiplier (domain-match + document-type bonuses).
- **Rerank:** cross-encoder `cross-encoder/ms-marco-MiniLM-L-6-v2`, `max_length=512`, `~0.1s/pair` on CPU. `final_score = sigmoid(logit)`.

**Models (must not change — see project memory):**
- Embeddings: `BAAI/bge-base-en-v1.5`, query prefix `"Represent this sentence for searching relevant passages: "`, `normalize_embeddings=True`.
- Reranker: `cross-encoder/ms-marco-MiniLM-L-6-v2`.
- Generation/analysis: **Gemini free-tier flash only** — `gemini-flash-lite-latest` (primary) with `gemini-3.6-flash` fallback. **Never a pro model.**

**Two independent pipelines** (this is a critical, easily-missed fact):

| | Sync `trigger_pipeline` | Streaming `trigger_pipeline_stream` |
|---|---|---|
| Transport | one-shot return | Server-Sent Events (`data: {...}\n\n`) |
| Quality gate | `validator.py` (`validate_response`, `calculate_retrieval_confidence`) + one regeneration | inline CIVIC JSON gate (empty-field ratio) — **does not import `validator.py`** |
| Default task | `QA` | `CIVIC` (from the Kanoon route) |
| Used by | `POST /api/kanoon/query` | `POST /api/kanoon/query-stream` (the live UI path) |

They **do not share** quality-gate code. The user-facing Kanoon experience is the **streaming** path.

---

## 3. Invariants — the contract that must be preserved

Any future change to retrieval must keep these true (downstream code depends on them):

1. `search()`, `search_sc_only()`, and the fusion helpers return `List[Dict]` where each dict has **`id`, `document`, `metadata`, `distance`**.
2. Each chunk's `metadata` must keep populating **`rrf_score`** — the confidence calculator (`validator.calculate_retrieval_confidence`) and the citation builder both read it. **After rerank, `rrf_score` is deliberately overwritten with the sigmoid `final_score`** (see A3/A4), so "rrf_score" downstream means "reranker probability," not the raw RRF sum.
3. Keep `retrieval_method` (`"hybrid"|"dense"|"sparse"` or `"dense+bm25"` on the SC path) and a rank field (`rrf_rank`).
4. **Citation numbering is positional and 1-based:** prompt header `[i+1]` corresponds to `chunks[i]`. Do **not** reorder chunks after `construct_prompt`, or citations will point to the wrong source.

---

## 4. Part A — Retrieval correctness fixes (A1–A5)

**File(s):** `BACKEND/app/knowledge/hybrid_retriever.py`, `BACKEND/app/knowledge/reranker.py`, `BACKEND/app/knowledge/chunking.py`
**Commits:** A1–A4 in `29646e0` (Phase 1); A5 in `0b22bef` (Phase 2, required re-ingest).

### A1 — Removed the absolute RRF threshold that starved the reranker

- **Problem.** The old code discarded fused candidates below an absolute RRF score (`MIN_RETRIEVAL_THRESHOLD = 0.015`). Because RRF sums are tiny (`1/(60+rank)` ≈ 0.016 for the top hit and shrinks fast), this left only ~7–14 candidates for the cross-encoder — far too few for the reranker to do useful work, and pathological for rare-term queries.
- **Fix.** Select candidates **by rank**, not by absolute score: take the top `RERANK_CANDIDATE_POOL = 30` fused candidates and hand all of them to the reranker.
- **As-built.** `_fuse_candidates()` sorts `rrf_scores` descending and slices `[:candidate_pool]` (`hybrid_retriever.py` §"4. Sort and apply Candidate Pool limit").

### A2 — Fixed the stale/leaked metadata multiplier in the sparse RRF loop

- **Problem.** In the sparse (BM25) fusion loop, the metadata multiplier was computed in one branch and the *previous* iteration's multiplier leaked into the `else` branch — so chunks were boosted by an unrelated chunk's domain/type match.
- **Fix.** Compute the multiplier **per-chunk, unconditionally**, via a single `calculate_metadata_multiplier(metadata)` helper used identically by both the dense and sparse loops.
- **As-built.** The helper (`hybrid_retriever.py` lines ~55–68) applies:
  - **Domain bonus:** `+ domain_multiplier_weight * predicted_domains[chunk_domain]` (weight default `0.10`, so ≤ ~+9% at confidence 0.9).
  - **Doc-type bonus:** flat `+0.05` when `document_type_priority != "any"` and the chunk's `document_type` matches.
  It is applied multiplicatively to each RRF term (`base_rrf * multiplier`), not once at the end.

### A3 + A4 — Unified all scoring on the cross-encoder sigmoid `final_score`

- **Problem (A3).** After the reranker returned chunks in cross-encoder order, the orchestrator re-sorted by `rrf_score`, **throwing away the reranker's ordering** — the single most valuable signal.
- **Problem (A4).** The SC path clamped logits with `max(0.01, logit)`, mixing a clamped-logit scale with real RRF sums, so SC chunks were truncated/compared on an inconsistent scale.
- **Fix.** Standardize every path on the reranker's calibrated probability:
  - `reranker.py` sets `reranker_score = logit` and `final_score = 1/(1+exp(-logit))` (sigmoid → `(0,1)`), and sorts descending by the logit (monotonic ⇒ same order as `final_score`).
  - Every retrieval entry point **mirrors `final_score` into `rrf_score`** after rerank, so downstream consumers keep working but now operate on the calibrated score:
    - `search()` (main path), `search_sc_only()` (SC path), and `_multi_query_retrieve()` (fan-out) all do `r["metadata"]["rrf_score"] = r["metadata"].get("final_score", ...)`.
- **Consequence.** The confidence calculator and citation builder now rank on reranker probability. Sorting is never undone after rerank.
- **Reranker failure mode (unchanged, documented):** if `model.predict` throws, `rerank()` returns `chunks[:top_k]` **unranked** with no `final_score`; downstream falls back to `rrf_score`/0.0.

### A5 — Fixed off-by-one section metadata in the structural chunker

- **File:** `BACKEND/app/knowledge/chunking.py` (`LegalStructuralChunker.chunk_text`). **Requires re-ingest** (metadata is baked into stored chunks).
- **Problem.** When a statute line matched a new `Section`/`Article`/`Chapter` boundary, the code updated `current_context` to the **new** section *before* flushing the buffered text of the **previous** section — so a chunk containing the *old* section's text got stamped with the *new* section number.
- **Fix.** Two-step ordering, now explicit in the code:
  1. Detect the boundary into a `pending` tuple **without mutating context**.
  2. **Flush the buffer under the current (old) context first** (lines ~52–57), *then* apply the new section and reset lower hierarchy levels (lines ~60–73).
- **As-built detail.** `_create_chunk()` enriches metadata (`part`/`chapter`/`section`/`article`) and prepends a human-readable context breadcrumb (`[SOURCE > Chapter X > Section Y] …`) to the chunk text to help dense retrieval. Chunk IDs are UUIDs.

---

## 5. Part B — Latency optimization (B1–B10)

**File(s):** `BACKEND/app/ai/orchestrator.py`, `hybrid_retriever.py`, `embeddings.py`, `bm25_manager.py`, `reranker.py`, `main.py`, `config.py`
**Commits:** B2/B3/B6/B7 in `29646e0`; B1/B1c/B4/B5/B8/B9 across `0b22bef` and `3d95fcc`; B10 is a standing decision.

### B1 — Overlap the analysis LLM with provisional retrieval (biggest streaming win)

- **Problem.** The streaming path ran serially: analysis LLM (~2.5 s) → then retrieval. The user saw nothing until both finished.
- **Fix.** In `trigger_pipeline_stream`, run the analysis LLM and a **provisional retrieval** concurrently on a 2-worker thread pool:
  ```python
  with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
      llm_future    = ex.submit(self._analyze_query_structured, question, history)
      search_future = ex.submit(provisional_search_task)
      query_analysis          = llm_future.result()
      query_embedding, prov_chunks = search_future.result()
  ```
- **`provisional_search_task`** runs `hybrid_retriever.search(question, q_emb, n_results=PROVISIONAL_N_RESULTS=12, where=filters, predicted_domains={}, candidate_pool=PROVISIONAL_CANDIDATE_POOL=14)` — a deliberately small pool so its rerank cost hides behind the ~2.5 s analysis call.
- **Seed reuse (safe).** The provisional search runs under the **same `filters`** as the main pass, so its chunks can be reused directly. On the fast path (`len(sub_queries) <= 1 and not explicit_sc and not predicted_domains`) the provisional chunks are returned as-is; otherwise they are passed as already-reranked **`seed_chunks`** into the fan-out, which subtracts the seed count from the rerank budget.

### B1c — Cap sub-queries

- `sub_queries` is truncated to `MAX_SUB_QUERIES = 3`. Prevents the analysis LLM's occasional 5-issue decomposition from multiplying retrieval/rerank work.

### B2 — Batch sub-query embeddings

- The fan-out embeds all sub-queries in **one** `embed_texts` call (each prefixed with the BGE query prefix, matching `embed_query`), instead of one embedding call per sub-query. On failure it reuses the base query embedding for all.

### B3 — Partial BM25 sort with `np.argpartition`

- **Problem.** `np.argsort` over the full BM25 score vector is O(N log N) across the entire corpus (tens of thousands of docs) just to take the top-K.
- **Fix.** `np.argpartition(scores, -k)[-k:]` then argsort only that slice — O(N) partition + O(k log k). Applied on both the main path (`k_sparse=30`) and the SC path (`k_sc=60`).

### B4 — Batch the cross-encoder + shrink the pool

- Reranker uses `model.predict(pairs, batch_size=RERANK_BATCH_SIZE=32)`.
- The fan-out reranks a merged pool capped at `RERANK_MERGED_POOL = 32` (minus seed count), instead of reranking each sub-query's pool separately.

### B5 — Warm heavy components at startup

- **File:** `main.py` lifespan. On boot it warms: the embedding model (`embedding_service.warmup()`), the global BM25 index (`bm25_manager.get_index("global")`), and the reranker. This moves cold-start cost off the first user request.

### B6 — Thread-safe BM25 rebuild + negative cache + atomic write

- **File:** `bm25_manager.py`. Two-tier cache (in-memory + on-disk pickle at `chroma_db/bm25_cache/bm25_<tenant>.pkl`) guarded by a `threading.Lock`. The pickle is written atomically (`.tmp` then `os.replace`). An `id_to_index` map is persisted (and back-filled on load) so BM25-only candidates can be reconstructed by id in O(1).

### B7 — Remove O(N) scans from candidate reconstruction

- **Problem.** Rebuilding the candidate dicts after fusion did linear scans over the corpus per candidate.
- **Fix.** Build `dense_by_id = {r["id"]: r for r in dense_results}` and a `sparse_id_set`, and use the persisted `id_to_index` for BM25-only reconstruction — all O(1) lookups.

### B8 — LRU-cache analysis + query embeddings

- `embed_query` is wrapped in `functools.lru_cache(maxsize=256)`.
- `_analyze_query_cached` is wrapped in `functools.lru_cache(maxsize=128)` and is used **only when there is no conversation history** (keyed on the normalized question). Crucially, it is designed to **let exceptions propagate** — `lru_cache` does not memoize exceptions, so a transient quota failure does not poison the cache with an empty result.

### B9 — Generation-path latency

- **Sync path** now passes `max_output_tokens` and only regenerates once (conditional on validation failure) rather than speculatively.
- **Output-token ceiling raised to 8192** (from 2048) at the streaming generation and `_generate_with_fallback` sites — the 2048 cap was truncating long CIVIC dossiers, which then failed the quality gate and triggered an expensive full regeneration. (This is the uncommitted `orchestrator.py` diff staged in this session: two `max_output_tokens=2048 → 8192` edits.)
- **Thinking-config fix (this session).** The plan assumed streaming already disabled "thinking" via `ThinkingConfig(disabled=True)`. In practice `disabled=True`, `thinking_budget=0`, and `thinking_level="none"` are all **rejected** by the SDK, and the resulting `ValidationError` was being swallowed — so thinking was never actually disabled. Introduced a `thinking_config(level)` helper that only emits a config when `level ∈ {"minimal","low"}` and returns `None` otherwise; all four LLM call sites now use `thinking_config(GEN/ANALYSIS_THINKING_LEVEL)` with the level set to `"minimal"`.
- **429/quota fallback (this session).** `_run_analysis_llm` iterates `ANALYSIS_MODELS = ("gemini-flash-lite-latest", "gemini-3.6-flash")`, skipping models currently in a 900 s cooldown. For each model it rotates up to `min(3, key_count)` API keys. On `429/RESOURCE_EXHAUSTED` it rotates keys, and after exhausting keys puts the **model** (not the key) into cooldown and falls through to the next flash model. It **raises** if everything is exhausted — deliberately, because a prior bug returned `"{}"` which silently collapsed the fan-out to a single generic query. (Free-tier quota is per-project-per-**model**, ~20 req/day, so retiring keys on 429 is wrong.)

### B10 — Stay CPU-only (decision)

- The reranker and embedder run on CPU. No GPU, no model downgrade. `TORCH_NUM_THREADS = 4` caps torch threads to avoid oversubscription. This was an explicit, owner-confirmed decision; latency work stayed within CPU constraints.

### The "rerank-once" fan-out (`_multi_query_retrieve`) — the core latency structure

This is the heart of commit `3d95fcc`. Old design reranked each sub-query's candidate pool separately (N × ~0.1 s/pair ⇒ 9–19 s). New design:

1. For each sub-query (≤3), call `_fuse_candidates` (cheap, ~0.08 s, **no rerank**) to get up to 30 fused candidates. If `explicit_sc_requested`, also fuse `_fuse_sc_candidates` per sub-query.
2. **Dedupe** the union by chunk `id`, tracking which sub-issues surfaced each chunk (`sub_issue_ids`); skip ids already covered by the reranked seeds.
3. Sort the union by `rrf_score`, then **round-robin across sub-issues** so no dominant sub-query starves the others; gather only `RERANK_MERGED_POOL - len(seed_chunks)` new candidates.
4. **Rerank ONCE** against the **primary (user) question** — not the sub-queries.
5. Merge with the already-reranked seed chunks, sort by `final_score`.
6. **Fair allocation** to a `target_total = 20`: guarantee `max(1, 20 // n_sub)` per sub-issue, then fill remaining slots by highest `final_score`.

> `target_total = 20` and RRF `k = 60` are **hard-coded**, not settings.

---

## 6. Supreme Court judgment ingestion

**Script:** `BACKEND/scripts/ingest_sc_judgments.py` (a faster variant exists: `ingest_sc_judgments_fast.py`).
**Source:** `BACKEND/data/judgments/*.json` (gitignored; 4,369 files on disk).
**Target collection:** `supreme_court_cases`.
**Result:** 4,367 judgments ingested → **58,689 chunks** (2 files failed; tracked in `scripts/ingestion_checkpoint.json`).

### How it works (per file, `process_file`)

1. **Parse JSON** and require a non-empty `text` field.
2. **Build base metadata** from the judgment JSON:
   `case_name` (`"{petitioner} v. {respondent}"`), `petitioner`, `respondent`, `judgment_date`, `bench`, `case_number`, `sections_cited`, `articles_cited` (both parsed from stringified lists via a safe `ast.literal_eval`), and fixed fields: `source_type="judgment"`, `authority_type="judicial"`, **`court_level="Supreme Court"`**, `jurisdiction="India"`, `source_file`. String fields are length-capped (e.g. `bench` ≤ 200).
3. **Case ID:** `case_id = f"SC_{basename_without_ext}"`. This `SC_` prefix is load-bearing — the SC retrieval path identifies SC chunks by `'SC_' in id` or `court_level == 'Supreme Court'`.
4. **Chunking:** a **local paragraph chunker** (not the statute `LegalStructuralChunker`): split on blank lines, greedily pack up to `max_chars=1600` with `overlap_chars=200` (overlap trimmed to a word boundary). Judgments are prose, so paragraph packing suits them better than section-structural parsing.
5. **Per-chunk:** `chunk_id = f"{case_id}_CHUNK_{i+1:06d}"`; metadata gets `case_id`, `chunk_index`, `total_chunks`; empty/`"None"` values are stripped. A **context prefix** is prepended to the embedded text:
   ```
   Case: {case_name}
   Court: Supreme Court of India

   {chunk}
   ```
6. **Embed** all chunk texts (`embedding_service.embed_texts`) and **store** with `vector_store.add_chunks(..., target_collection="supreme_court_cases")`.

### Resumability

- `ingestion_checkpoint.json` tracks `completed_files` / `failed_files`; the run skips completed files and saves progress every 10 files, logging throughput + ETA. This is how a 4,369-file ingest was run incrementally.

### Related SC utilities

- `scripts/backfill_sc_domain.py` — back-fills `legal_domain` onto SC chunks (used by the domain-filter `where` clause on the SC path).
- `scripts/rebuild_bm25.py` — rebuilds the global BM25 index after ingestion (the global index includes the SC collection).

---

## 7. Statute/scheme corpus ingestion & structural chunking

**Script:** `BACKEND/scripts/ingest_corpus.py`. **Source:** `BACKEND/corpus/*.md|*.txt` (100 files). **Target:** `nyaay_knowledge` (default collection) → **8,246 chunks**.

- **Deduplication by content hash.** Before ingesting, it reads all existing `file_hash` metadata from the collection; each corpus file's SHA-256 is computed and **skipped if already present**, so re-runs are idempotent and versioned (a changed file = new hash = re-ingested).
- **Base metadata:** `source_name` (filename upper-cased), `document_id`, `file_hash`, `ingestion_timestamp`, `tenant_id="global"`, and a coarse `type` (`"statute"` if the name contains `BNS`/`CONSTITUTION`/`BSA`, else `"judgment"`).
- **Chunking:** uses `semantic_chunker` = `LegalStructuralChunker` (the A5-fixed structural chunker) — splits along `PART`/`CHAPTER`/`SECTION`/`ARTICLE` boundaries, `max_chunk_size=1500`, `overlap=200`, and enriches each chunk with `part`/`chapter`/`section`/`article` metadata + a breadcrumb prefix.
- **BM25 once at the end.** To save time it bypasses per-document BM25 rebuilds and calls `bm25_manager.rebuild_index("global")` **once** after all files are processed.
- **Schemes:** `scripts/ingest_schemes.py` and `ingest_schemes_batch_2.py` ingest welfare-scheme documents into the same `nyaay_knowledge` collection (welfare/CIVIC content). `ingest_mta.py` ingests a specific act.

> Corpus files include the new criminal codes (`BHARATIYA_NYAYA_SANHITA_2023.md`, `BSA_2023.md`, `Bharatiya_Nagarik_Suraksha_Sanhita.md`) alongside ~100 core acts (CrPC, CPC, Companies Act, Competition Act, GST, Arms Act, etc.).

---

## 8. Generation path & quality gates

### Sync pipeline (`trigger_pipeline`, task defaults to `QA`)

1. Guardrails → complexity estimate (`CIVIC` ⇒ always complex; else regex for SC/precedent, multi-domain, or >100 words).
2. Complex ⇒ structured analysis → `_multi_query_retrieve(primary_query=question)`. Simple ⇒ single-shot expansion → `hybrid_retriever.search(n_results=10)`.
3. **Confidence:** `validator.calculate_retrieval_confidence(chunks, query_analysis)` returns a score/label from a rule table:
   - statute **and** judgment **and** domain-matched → **95 / 🟢 High**
   - statute **and** domain-matched → **80 / 🟢 High**
   - statute, not domain-matched → **55 / 🟡 Moderate**
   - SC requested but no judgment retrieved → **40 / 🟠 Limited**
   - judgment only → **75 / 🟡 Moderate**; else **60 / 🟠 Limited**; empty → **0 / 🔴 Insufficient**
4. **Generate** via `_generate_with_fallback` (`max_retries=2`, `CIVIC_MODEL`, `max_output_tokens=8192`, thinking `minimal`; drops dead keys on daily-quota errors, sleeps 0.5 s on other 429s and reports accumulated sleep so it can be subtracted from "model processing" latency).
5. **Validate + one repair:** `validate_response` fails if the answer is `< 50` chars or contains a hallucinated `"NN% likelihood"` probability; on failure it regenerates once, then falls back.

### Streaming pipeline (`trigger_pipeline_stream`, task = `CIVIC` from Kanoon)

- Emits early metadata (authorities/doc-type harvested from the first 3 chunks), then runs generation on a **background thread** feeding a `queue.Queue`, with a **25 s SLA deadline** in the reader loop.
- **CIVIC does not stream per-token frames** to the client (`if task_type != "CIVIC": yield ... 'chunk'`); it accumulates the full JSON dossier and emits it as one frame plus a `complete` frame with citations/metrics.
- **CIVIC quality gate (inline, not in `validator.py`).** Parses the JSON; if `> 60%` of the fields across `problemAndRights` + `relevantAuthority` are empty or `"Not established from retrieved authority"`, it emits `SYNTHESIS_FAILURE: …` and returns. A JSON parse failure emits `SYNTHESIS_FAILURE: Failed to generate a structured case dossier.` The **"Not established…"** sentinel originates in the CIVIC system prompt (`prompt_builder.py`).
- **Citations:** a chunk is cited if its `[n]` marker is used **or if no markers were found at all** — so CIVIC JSON (which uses no `[n]` markers) surfaces all retrieved chunks as sources.

### Prompt construction (`prompt_builder.py`)

- Four system prompts: `QA` (markdown `## Executive Summary` + `## Detailed Answer`), `DRAFTING`, `CIVIC` (raw JSON dossier), `REASONING` (raw JSON).
- **Evidence compression is CIVIC-only** (`compress_evidence`, `max_chars=5000`): dedupe by Jaccard word-overlap > 0.8, score by position + query-term overlap, greedily budget to 5000 chars, then **re-sort by original index** so **citation numbers stay stable**. QA/REASONING/DRAFTING pass full chunk text with no token budget.
- **Citation headers are 1-based** (`[i+1]`) and formatted `--- [n] SUPREME COURT | {src} ---` for judgments or `--- [n] STATUTE | {src} — Section {s} ---` for statutes.
- **Prompt-injection defense:** user text is wrapped in `<user_input>…</user_input>` with an explicit instruction to disregard instructions inside the tags.

---

## 9. Frontend rendering changes

**Files:** `FRONTEND/src/components/kanoon/KanoonRenderer.jsx`, `reasoning/LegalAnalysisRenderer.jsx`, `uploadChat/UploadChatRenderer.jsx` (uncommitted; staged this session).

**Why.** The streaming CIVIC path returns a JSON dossier as text. LLM JSON is frequently *almost* valid — wrapped in prose or ```` ``` ```` fences, with trailing commas or unescaped newlines — and a naive `JSON.parse` throws, blanking the UI.

**Fix (all three renderers).** Before parsing:
1. `trim()`, then slice to the outer object: `substring(indexOf('{'), lastIndexOf('}')+1)`.
2. Strip trailing commas: `replace(/,\s*([}\]])/g, '$1')`.
3. `LegalAnalysisRenderer` additionally **escapes stray control chars inside string values** (`\n`,`\r`,`\t` → escaped) via a string-aware regex, and logs the offending content to the console on failure.

Result: robust rendering of real-world LLM JSON instead of a blank panel on the first malformed field.

---

## 10. Configuration reference

**File:** `BACKEND/app/core/config.py`. Settings added/used by this work (verified live):

| Setting | Value | Role |
|---|---|---|
| `CIVIC_MODEL` | `gemini-flash-lite-latest` | generation model (CIVIC + fallback) |
| `RERANK_CANDIDATE_POOL` | `30` | fused candidates per (sub-)query handed to rerank |
| `RERANK_MERGED_POOL` | `32` | cap on the merged fan-out pool reranked once |
| `PROVISIONAL_CANDIDATE_POOL` | `14` | small pool for the streaming provisional search |
| `PROVISIONAL_N_RESULTS` | `12` | provisional search result count |
| `MAX_SUB_QUERIES` | `3` | cap on analysis-produced sub-queries |
| `RERANK_BATCH_SIZE` | `32` | cross-encoder `predict` batch size |
| `TORCH_NUM_THREADS` | `4` | torch thread cap (CPU) |
| `ANALYSIS_THINKING_LEVEL` | `minimal` | thinking level for analysis LLM |
| `GEN_THINKING_LEVEL` | `minimal` | thinking level for generation LLM |

Hard-coded (not settings): RRF `k = 60`, fan-out `target_total = 20`, dense `initial_k = 20` (main) / `30` (SC), BM25 top-`k` `30` (main) / `60` (SC).

---

## 11. Commit history mapping

| Commit | Title | Contents |
|---|---|---|
| `29646e0` *(on `main`)* | Phase 1: Retrieval correctness fixes (A1–A4, B2, B3, B6, B7, Part C) | Core correctness (A1–A4) + early latency wins + config scaffolding |
| `0b22bef` | RAG phase 2-4: streaming latency, chunking fix, config cleanup | B1 overlap, A5 chunking fix (re-ingest), config/dead-code cleanup |
| `3d95fcc` *(branch HEAD)* | RAG latency: rerank-once fan-out, analysis 429 fallback, thinking fix | `_multi_query_retrieve` rerank-once, model-fallback on 429, thinking-config helper |
| *(uncommitted)* | staged in this session | `orchestrator.py` `max_output_tokens` 2048→8192 ×2; 3 frontend JSON-robustness renderers; `DOCS/RAG_IMPROVEMENT_PLAN.md`; this report; benchmark/profiling scripts |

**Branch diff `main...HEAD` touched:** `orchestrator.py` (+469 lines of churn), `hybrid_retriever.py` (71), `chunking.py` (34), `config.py` (25), `main.py` (14), `embeddings.py` (6), `reranker.py` (4), `validator.py` (4), plus `scripts/baseline_metrics.json` and `scripts/ingestion_checkpoint.json`.

---

## 12. Verification & benchmarking

**Code integrity (this session):** `py_compile` passes for all key modules; all modules (config, validator, chunking, prompt_builder, vector_store, bm25_manager, hybrid_retriever, orchestrator) import cleanly with `EXIT=0`; the full app was previously run healthy on `:8000`.

**No-regression proof.** The deterministic retrieval benchmark (`scripts/bench_multiquery.py`, `deterministic_benchmark.py`) produced **byte-identical SC chunk counts before and after** the edits — proof that the `rrf_rank`/`where=filters`/mirroring changes did not alter retrieval results.

**Pool-trim experiment (rejected).** Shrinking `RERANK_MERGED_POOL` 32→24 made sync latency *worse* (4.17 s → 5.60 s) and dropped SC counts on several test queries. Kept `32`.

**Benchmark caveat.** Back-to-back benchmark runs showed latency roughly *double* (sync ~8 s, stream ~4 s) on the second run — diagnosed as CPU contention/thermal throttling on the loaded dev laptop, **not** a regression, because the retrieval result sets were byte-identical across the runs. Benchmarking was stopped to spare the machine.

**Benchmark/profiling tooling added** (under `BACKEND/scripts/`): `bench_multiquery.py`, `bench_e2e.py`, `deterministic_benchmark.py`, `profile_stream.py`, `test_smoke.py`, `run_benchmark_3x.ps1`. Their JSON outputs (`*_metrics.json`, `_profile_*.json`) are transient and were **not** committed.

---

## 13. Known discrepancies & future work

Flagged during the as-built review — **not yet fixed**, recorded so they aren't lost:

1. **RRF offset inconsistency.** Main path uses `1/(60+rank)` (0-indexed); SC path uses `1/(60+rank+1)` (1-indexed). Harmless in practice (RRF only needs monotonic ranking) but inconsistent; unify if touched.
2. **Sync Kanoon uses `QA`, not `CIVIC`.** `kanoon_service.query()` calls `trigger_pipeline` **without `task_type`**, so the non-streaming endpoint produces QA markdown while the streaming endpoint produces a CIVIC dossier, and it skips the acronym expansion the streaming path does. Likely unintended — verify before relying on the sync endpoint.
3. **`GEN_THINKING_LEVEL` dead fallback.** Call sites use `getattr(settings, "GEN_THINKING_LEVEL", "low")` while the setting is `"minimal"`. The `"low"` literal is a dead fallback; effective value is `"minimal"`.
4. **`search_sc_only()` appears legacy.** No orchestrator caller in the reviewed paths (the fan-out calls `_fuse_sc_candidates` directly). Confirm before deleting.
5. **`validator.py` is sync-only.** The streaming (user-facing) path has no confidence score or hallucinated-percentage guard — only the CIVIC empty-field gate. Consider porting `validate_response` to streaming.
6. **Out-of-scope cleanup still pending** (from the plan): `_filter_relevant_chunks` is dead code; unused `_bm25_cache`/`_corpus_cache` were removed but audit for others; `nltk.download` at import performs a network call at startup — make it offline-safe/vendored.
7. **Generation is the latency floor.** ~6.5 s of ~13 s is output-token-bound on free-tier flash. Further latency gains require shorter answers (product decision: keep detail) or a faster model tier (constrained to free flash by project policy).

---

## 14. Operational procedures (re-ingest, rebuild, run)

### Re-ingest from scratch (e.g. after a chunker change like A5)

```bash
# 1. Back up the current vector DB (do NOT commit the backup — 228MB binary)
#    e.g. copy BACKEND/chroma_db -> BACKEND/chroma_db_backup

# 2. Clear chroma_db/ (both collections) — or delete the collections programmatically

# 3. Re-run ingestion (from BACKEND/)
python scripts/ingest_corpus.py          # statutes + core acts -> nyaay_knowledge
python scripts/ingest_schemes.py         # welfare schemes -> nyaay_knowledge
python scripts/ingest_sc_judgments.py    # SC judgments -> supreme_court_cases (resumable via checkpoint)

# 4. Rebuild the global BM25 index (includes the SC collection)
python scripts/rebuild_bm25.py
```

> `chroma_db/` and the corpus/judgment data dirs are gitignored. `chroma_db_backup/` is **not** gitignored by default — exclude it manually (it is 228 MB of binary and exceeds GitHub's file-size limit).

### Run the app

```bash
# Backend (FastAPI, warms models on startup) — from BACKEND/
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

```bash
# Frontend (Vite/React) — from FRONTEND/
npm run dev   # serves http://localhost:3000 (host 127.0.0.1)
```

> **Auth note.** Firebase authorizes `localhost` by default but **not** `127.0.0.1` — open the app at **`http://localhost:3000`** to avoid `auth/unauthorized-domain`. CORS allows only `localhost`/`127.0.0.1` on ports `3000`/`5173` (not `3001`).

---

*End of report.*
