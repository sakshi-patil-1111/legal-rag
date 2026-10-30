# NYAAY AI — RAG Pipeline Improvement Plan (Implementation Handoff)

**Audience:** implementing agent (Antigravity Gemini 3.1 Pro, high).
**Goal:** make retrieval **accurate** (fix scoring/fusion/chunking bugs that silently drop recall) and **fast** (cut end-to-end latency without reducing answer quality).
**Scope:** backend only (`BACKEND/app/knowledge/**`, `BACKEND/app/ai/orchestrator.py`, `BACKEND/app/core/config.py`, `BACKEND/app/main.py`). Frontend and auth are out of scope.

> This document is self-contained. Every change lists the file, the exact location, the problem, the corrected code/behavior, and why it is safe. Follow the **phase order** — Phase 1 needs no re-ingest, Phase 2 requires re-ingesting the corpus, Phase 3 is architectural latency work.

---

## 0. System recap (so you don't have to re-derive it)

Two public entry points on `RAGOrchestrator` (`app/ai/orchestrator.py`):

- `trigger_pipeline(...)` — **synchronous**, used by `/api/kanoon` non-streaming query.
- `trigger_pipeline_stream(...)` — **SSE streaming**, used by the Civic Navigator (`task_type="CIVIC"`).

Pipeline stages (streaming path, the important one):

1. `_analyze_query_structured()` → **1 blocking Gemini call** returning `sub_queries`, `domains`, `explicit_sc_requested`. **Runs before any retrieval.**
2. `embed_query()` on the first sub-query (BGE-base, CPU).
3. `_multi_query_retrieve()` → for each sub-query, in a 4-thread pool, calls `hybrid_retriever.search()`:
   - dense search over 2 Chroma collections (`nyaay_knowledge` + `supreme_court_cases`),
   - BM25 full-corpus scan,
   - RRF fusion + metadata multipliers,
   - **absolute score threshold**,
   - cross-encoder rerank (`ms-marco-MiniLM-L-6-v2`, CPU).
4. `construct_prompt()` (Python).
5. **1 Gemini streaming call** for the answer.

Latency ranking (largest first): (a) the blocking analysis LLM call, (b) CPU embeddings + cross-encoder rerank done per sub-query, (c) BM25 full scan+sort per sub-query, (d) generation. The vector DB itself is not the bottleneck.

**Invariants you must preserve (downstream readers depend on them):**
- `hybrid_retriever.search()` / `search_sc_only()` must keep returning `List[Dict]` with keys `id`, `document`, `metadata`, `distance`.
- `metadata` must keep populating **`rrf_score`** — `app/ai/validator.py::calculate_retrieval_confidence` and the citation builder in `orchestrator.py` read it. If you add a new `final_score`, keep writing `rrf_score` too (set it equal to the normalized final score is fine).
- `metadata["retrieval_method"]`, `metadata["rrf_rank"]` / `retrieval_rank` are read for citations — keep them.
- Citation marker numbering is positional (`chunks[i]` → `[i+1]`). Don't reorder chunks after `construct_prompt` builds the prompt.

**Pre-flight check (do this first, 5 min):** the code calls model IDs `gemini-3.6-flash`, `gemini-3.6-pro` (`orchestrator.py`, `drafting_orchestrator.py`) and `gemini-flash-lite-latest` (`config.py:18`). Verify these are valid, currently-available Gemini model IDs against the API. A wrong ID fails at request time and the retry loop only retries on HTTP 503, so it would surface as a hard failure. Fix any invalid IDs before benchmarking, otherwise your before/after numbers are meaningless.

---

## PART A — Accuracy & correctness fixes (Phase 1, no re-ingest)

### A1. Remove the absolute RRF threshold that starves the reranker
**File:** `app/knowledge/hybrid_retriever.py`, lines ~92–99 (in `search()`).

**Problem.** A single-source RRF score is exactly `1/(60+rank)`. The threshold `MIN_RETRIEVAL_THRESHOLD = 0.015` (`config.py:19`) therefore admits only ranks 0–6 (`1/67 = 0.0149 < 0.015`). You broaden dense to 20 and take BM25 top-30, but the cross-encoder usually receives only ~7–14 candidates; the `[:20]` cap is dead. An absolute cutoff on RRF is a category error — RRF encodes *rank*, not *relevance*, so the number carries no information about chunk quality. It also interacts with the metadata multiplier so that only domain-boosted chunks get deep recall.

**Fix.** Delete the threshold gate. Select a fixed candidate pool by rank and let the cross-encoder judge relevance (that is its job).

Replace:
```python
sorted_rrf = sorted(rrf_scores.items(), key=lambda item: item[1], reverse=True)
threshold = getattr(settings, "MIN_RETRIEVAL_THRESHOLD", 0.005)
filtered_ids = [item[0] for item in sorted_rrf if item[1] >= threshold]
top_ids = filtered_ids[:20]
```
with:
```python
sorted_rrf = sorted(rrf_scores.items(), key=lambda item: item[1], reverse=True)
candidate_pool = getattr(settings, "RERANK_CANDIDATE_POOL", 30)
top_ids = [cid for cid, _ in sorted_rrf[:candidate_pool]]
```

**Optional quality floor (recommended):** after reranking, drop only clear junk using a *calibrated reranker* score, not RRF. See A4 for the `final_score` (sigmoid of the cross-encoder logit); then filter `final_score >= RERANK_SCORE_FLOOR` with `RERANK_SCORE_FLOOR = 0.02` default. This removes obvious non-matches while keeping recall.

**Why safe:** the cross-encoder is a stronger relevance signal than an RRF cutoff; you are giving it more candidates, not fewer, and still returning `n_results` at the end.

---

### A2. Fix the stale metadata multiplier in the sparse RRF loop
**File:** `app/knowledge/hybrid_retriever.py`, lines ~79–90 (in `search()`).

**Problem.** In the sparse loop, the `else` branch (chunk already seen in the dense pass) does `rrf_scores[chunk_id] += (base_rrf * multiplier)` but never computes `multiplier` for the current chunk — it reuses whatever value leaked from a prior iteration. Hybrid hits (the chunks you most want ranked right) get a *different* chunk's boost.

**Fix.** The metadata multiplier is a property of the chunk, identical whether the chunk came from dense or sparse. Compute it once per iteration and add the sparse rank contribution consistently.

Replace the sparse loop:
```python
sparse_ranking = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)
for rank, idx in enumerate(sparse_ranking[:30]):
    chunk_id = corpus_ids[idx]
    base_rrf = (1.0 / (60 + rank))
    if chunk_id not in rrf_scores:
        multiplier = calculate_metadata_multiplier(corpus_metadatas[idx])
        rrf_scores[chunk_id] = (base_rrf * multiplier)
    else:
        rrf_scores[chunk_id] += (base_rrf * multiplier)
```
with:
```python
# Top-30 sparse by BM25 score (argpartition avoids full sort — see B3)
import numpy as np
k_sparse = 30
if len(bm25_scores) > k_sparse:
    top_idx = np.argpartition(bm25_scores, -k_sparse)[-k_sparse:]
    sparse_ranking = top_idx[np.argsort(bm25_scores[top_idx])[::-1]]
else:
    sparse_ranking = np.argsort(bm25_scores)[::-1]

for rank, idx in enumerate(sparse_ranking):
    idx = int(idx)
    chunk_id = corpus_ids[idx]
    base_rrf = 1.0 / (60 + rank)
    multiplier = calculate_metadata_multiplier(corpus_metadatas[idx])  # always for THIS chunk
    rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + (base_rrf * multiplier)
```
Keep `sparse_ranking` available for the "is_sparse" membership check later — but convert that check to a `set` (see B7).

**Why safe:** dense and sparse contributions now use the same, correct per-chunk multiplier; hybrid chunks get exactly `(dense_rrf + sparse_rrf) * multiplier`.

---

### A3 + A4. Unify final scoring on the cross-encoder scale (fixes reranker-order loss AND SC score mismatch)
**Files:** `app/knowledge/hybrid_retriever.py` (`search`, `search_sc_only`), `app/ai/orchestrator.py` (`_multi_query_retrieve`).

**Problem A3.** `search()` returns chunks ordered by cross-encoder score, but `_multi_query_retrieve` re-sorts by `rrf_score` (`orchestrator.py:193`), demoting the reranker to a filter and discarding its ordering — which is what determines what the LLM emphasizes.

**Problem A4.** `search_sc_only` maps reranker **logits** (~−11…+11) into `rrf_score` via `max(0.01, logit)` (`hybrid_retriever.py:224`). Most logits clamp to `0.01`, then get compared against real RRF (~0.0167) in the dedup/sort — so Supreme Court chunks systematically lose the merge.

**Root cause:** two incomparable scales (RRF rank-scores vs cross-encoder logits) are mixed in one sort.

**Fix (single unifying change):** after every rerank, write a normalized `final_score = sigmoid(reranker_logit)` into metadata, and make the multi-query merge sort/dedupe by `final_score`. Keep writing `rrf_score` for backward compat.

1. In `app/knowledge/reranker.py::rerank`, after computing `scores`:
```python
import math
for i, chunk in enumerate(chunks):
    logit = float(scores[i])
    chunk["metadata"]["reranker_score"] = logit
    chunk["metadata"]["final_score"] = 1.0 / (1.0 + math.exp(-logit))  # sigmoid -> (0,1)
```
2. In `hybrid_retriever.search()`, after `final_results = reranker_service.rerank(...)`, mirror `final_score` into `rrf_score` so downstream confidence/citation code keeps working:
```python
for r in final_results:
    r["metadata"]["rrf_score"] = r["metadata"].get("final_score", r["metadata"].get("rrf_score", 0.0))
```
3. In `hybrid_retriever.search_sc_only()`, replace the clamp block:
```python
for chunk in ranked_sc:
    chunk["metadata"]["rrf_score"] = max(0.01, chunk["metadata"].get("reranker_score", 0.0))
```
with:
```python
for chunk in ranked_sc:
    chunk["metadata"]["rrf_score"] = chunk["metadata"].get("final_score", 0.0)  # already 0..1 sigmoid
```
4. In `orchestrator.py::_multi_query_retrieve`, change **both** the tie-break (line ~177) and the sort (line ~193) from `rrf_score` to `final_score`:
```python
# tie-break when the same chunk is found by multiple sub-queries
if r.get("metadata", {}).get("final_score", 0) > dedup_map[cid].get("metadata", {}).get("final_score", 0):
    ...
# global ordering
unique_results.sort(key=lambda x: x.get("metadata", {}).get("final_score", 0), reverse=True)
```

**Why safe:** all comparisons are now cross-encoder-to-cross-encoder on a bounded `(0,1)` scale; dense-only, sparse-only, and SC chunks compete fairly. `rrf_score` still exists for `calculate_retrieval_confidence` and citation payloads.

> Note: cross-encoder scores across *different* sub-queries are approximately comparable (same model, "relevance of doc to a query"). This is standard practice for multi-query RAG and is strictly better than the current RRF re-sort.

---

### A5. Fix off-by-one section metadata in the chunker  *(Phase 2 — requires re-ingest)*
**File:** `app/knowledge/chunking.py`, `chunk_text()` lines ~43–61 and `_create_chunk`.

**Problem.** `current_context[...]` is updated **on match** (line ~48) *before* the buffer is flushed (line ~59). The flushed chunk contains the **previous** section's text but is stamped with the **new** section number. Every structural boundary mislabels one chunk, and those labels feed `get_canonical_source_name` → user-facing citations, so the app can cite the wrong section. Two secondary bugs: (i) the `char_count > 200` gate merges a short section into the next under one (wrong) label; (ii) lower hierarchy levels (`Section`/`Article`) are never reset when a new `Chapter`/`Part` begins, so chunks inherit stale sections.

**Fix.** Detect the boundary without mutating context; flush the buffer under the **old** context; then apply the update and reset lower levels.

Replace the per-paragraph structural block:
```python
structure_changed = False
for key, pattern in self.patterns.items():
    match = re.match(pattern, para)
    if match:
        current_context[key.capitalize()] = match.group(1)
        if key in ["section", "article"]:
            current_context["Heading"] = para
        structure_changed = True
        break

if structure_changed and lines_buffer:
    if char_count > 200:
        chunks.append(self._create_chunk(lines_buffer, current_context, base_metadata))
        lines_buffer = []
        char_count = 0

lines_buffer.append(para)
char_count += len(para) + 1
```
with:
```python
# 1. Detect a structural boundary WITHOUT mutating context yet.
pending = None  # (ContextKey, value, is_section_or_article, heading_line)
for key, pattern in self.patterns.items():
    match = re.match(pattern, para)
    if match:
        pending = (key.capitalize(), match.group(1), key in ("section", "article"), para)
        break

# 2. On a boundary, flush the buffer under the CURRENT (old) context so the
#    just-ended section's text is not mislabeled with the new section number.
if pending and lines_buffer:
    is_section_boundary = pending[2]
    if is_section_boundary or char_count > 200:
        chunks.append(self._create_chunk(lines_buffer, current_context, base_metadata))
        lines_buffer = []
        char_count = 0

# 3. Now apply the update for the NEW section and reset lower hierarchy levels.
if pending:
    ctx_key, ctx_val, is_heading, heading_line = pending
    current_context[ctx_key] = ctx_val
    if ctx_key == "Part":
        current_context["Chapter"] = None
        current_context["Section"] = None
        current_context["Article"] = None
        current_context["Heading"] = None
    elif ctx_key == "Chapter":
        current_context["Section"] = None
        current_context["Article"] = None
        current_context["Heading"] = None
    if is_heading:
        current_context["Heading"] = heading_line

lines_buffer.append(para)
char_count += len(para) + 1
```

**Also remove dead state:** `current_chunk = ""` (unused) and honor the constructor `overlap` param or delete it (currently hardcoded to "last 2 lines"; either wire `self.overlap` in or drop the param to avoid the lie).

**Re-ingest required:** metadata is baked at ingest time, so this change only takes effect after re-running ingestion. See §C "Re-ingest procedure."

**Why safe:** flushing on section boundaries yields chunks whose stamped section matches their text; `max_chunk_size` still bounds the top end. Chunk count may rise modestly (correctly).

---

## PART B — Latency reduction (no quality loss)

### B1. Overlap the blocking analysis LLM call with retrieval  *(biggest streaming win)*
**File:** `app/ai/orchestrator.py::trigger_pipeline_stream` (and mirror in `trigger_pipeline`).

**Problem.** `_analyze_query_structured()` is a full Gemini call (~1–3 s) that completes **before** embedding/retrieval start. This is the dominant wall-clock cost and makes the advertised "<500 ms TTFT" impossible.

**Fix (recommended, quality-preserving):** run analysis and a provisional retrieval concurrently.
- Immediately embed the **raw question** and launch a provisional `hybrid_retriever.search(raw_question, ...)` in a thread (so vector + rerank work happens *during* the analysis call).
- Concurrently call `_analyze_query_structured()`.
- When analysis returns, run `_multi_query_retrieve()` on the sub-queries; **merge** with the provisional results (dedupe by `id`, keep max `final_score`). Reuse the provisional embedding for the sub-query whose text ≈ the raw question.
- Keep emitting the same SSE status events ("Analyzing intent…", "Searching legal corpus…").

Net effect: the 1–3 s analysis is hidden behind retrieval instead of stacked before it.

**Lower-risk fallback** (if you don't want the concurrency merge): keep the sequence but (a) cap `sub_queries` to 3 (B1c) and (b) batch-embed them (B2). Smaller win, trivial change.

**B1c.** Cap sub-queries: in `_multi_query_retrieve`, `sub_queries = sub_queries[: getattr(settings, "MAX_SUB_QUERIES", 3)]`. Each sub-query is a full dense+BM25+rerank fan-out; 5 → 3 cuts retrieval work ~40%.

---

### B2. Batch sub-query embeddings (stop the per-query loop)
**File:** `app/ai/orchestrator.py::_multi_query_retrieve`, lines ~122–128.

**Problem.** Sub-queries are embedded one at a time in a Python loop, each a separate model invocation.

**Fix.** One batched call. BGE encodes batches efficiently.
```python
# BGE query prefix must be applied per query (embed_query does this); batch via embed_texts.
prefix = "Represent this sentence for searching relevant passages: "
try:
    embeddings = embedding_service.embed_texts([prefix + sq for sq in sub_queries])
except Exception:
    embeddings = [base_query_embedding] * len(sub_queries)
```
(Confirm `embed_query` uses exactly this prefix — it does, `embeddings.py:51` — so batching reproduces identical vectors.)

---

### B3. Replace full BM25 sorts with partial selection
**Files:** `app/knowledge/hybrid_retriever.py` (`search` — folded into A2 above; `search_sc_only` lines ~173–174).

**Problem.** `sorted(range(len(scores)), ...)` is O(N log N) over the whole corpus, per sub-query, ×4 threads.

**Fix.** Use `np.argpartition` for top-k (shown in A2). In `search_sc_only` do the same for `top_bm25_indices`. This is a pure speed change, identical results.

---

### B4. Batch the cross-encoder and shrink the candidate pool
**Files:** `app/knowledge/reranker.py`, `app/knowledge/hybrid_retriever.py`.

- In `reranker.py::rerank`, set an explicit batch size: `scores = self.model.predict(pairs, batch_size=getattr(settings, "RERANK_BATCH_SIZE", 32))`.
- Candidate pool of 30 (A1) is a good balance; do not exceed ~30 on CPU — rerank cost is linear in pairs.
- (Optional, larger change) Convert the cross-encoder to ONNX / int8 for a ~2–4× CPU speedup with negligible quality change. Only if CPU-bound after the above.

---

### B5. Warm up ALL heavy components at startup (not just embeddings)
**File:** `app/main.py`, `lifespan()` (currently only calls `embedding_service.warmup()`).

**Problem.** The cross-encoder loads lazily on first `search()` (imported inside the function), and the global BM25 index builds on first cache miss — both land on the **first real user request**, contradicting the "cold-start eliminated" claim.

**Fix.** In `lifespan` startup, after embedding warmup:
```python
from app.knowledge.reranker import reranker_service   # forces CrossEncoder load
from app.knowledge.bm25_manager import bm25_manager
bm25_manager.get_index("global")                       # build/load global BM25 once
# tiny end-to-end warm pass to trigger torch/thread init:
try:
    reranker_service.rerank("warmup", [{"document": "warmup", "metadata": {}}], top_k=1)
except Exception:
    pass
```
Wrap in try/except so a warm failure never blocks startup.

---

### B6. Thread-safe BM25 rebuild + cache negative results
**File:** `app/knowledge/bm25_manager.py`.

**Problem.** `_multi_query_retrieve` calls `search()` from 4 threads; on a cold cache all four can enter `rebuild_index()` at once, each doing a full corpus load + tokenize + `pickle.dump` to the *same path* → possible truncated/corrupt pickle. Also, empty-tenant results are never cached, so every request for a doc-less tenant re-scans Chroma.

**Fix.**
```python
import threading
class BM25Manager:
    def __init__(self):
        ...
        self._lock = threading.Lock()

    def get_index(self, tenant_id="global"):
        if tenant_id in self._memory_cache:
            data = self._memory_cache[tenant_id]
            return data["bm25"], data["corpus_ids"], data["corpus_docs"], data["corpus_metadatas"]
        with self._lock:
            # re-check inside the lock (another thread may have built it)
            if tenant_id in self._memory_cache:
                data = self._memory_cache[tenant_id]
                return data["bm25"], data["corpus_ids"], data["corpus_docs"], data["corpus_metadatas"]
            # ... existing disk-load then rebuild logic ...
```
In `rebuild_index`, on the "no documents" branch, cache an empty sentinel so it isn't rebuilt every call:
```python
if not corpus_docs:
    self._memory_cache[tenant_id] = {"bm25": None, "corpus_ids": [], "corpus_docs": [], "corpus_metadatas": [], "id_to_index": {}}
    return
```
Write the pickle atomically: dump to `cache_path + ".tmp"` then `os.replace(tmp, cache_path)`.

---

### B7. Remove O(N) scans in candidate reconstruction
**File:** `app/knowledge/hybrid_retriever.py::search`, lines ~101–135, and `bm25_manager.py`.

**Problem.** `corpus_ids.index(cid)` (line ~124), the nested `for res in dense_results` (line ~105), and the sparse membership loop (line ~111) are each O(N) or O(K·N) per query.

**Fix.**
- Build once per search: `dense_by_id = {r["id"]: r for r in dense_results}` and `sparse_id_set = {corpus_ids[int(i)] for i in sparse_ranking}`.
- Store an `id_to_index` map in the BM25 cache payload (build it in `rebuild_index`: `"id_to_index": {cid: i for i, cid in enumerate(corpus_ids)}`; return it from `get_index`). Use it instead of `corpus_ids.index(cid)`.
- Rewrite the reconstruction loop to O(K) lookups.

---

### B8. (Optional) LRU-cache query analysis and query embeddings
**File:** `app/ai/orchestrator.py`, `app/knowledge/embeddings.py`.

Add a bounded `functools.lru_cache`-style cache keyed by normalized (lowercased, stripped) question for `_analyze_query_structured` output and for `embed_query`. Helps repeated/demo queries and identical retries. Low risk; put a size cap (e.g. 256) and skip caching when `history` is present (context-dependent).

---

### B9. Generation-path latency
**File:** `app/ai/orchestrator.py`.

- `trigger_pipeline` (sync) has no `max_output_tokens` and regenerates the whole answer on validation failure — doubling latency. Add `max_output_tokens` (match the 2048 used in streaming) and make regeneration conditional (only on hard schema failure, not soft).
- Prefer routing clients to the streaming endpoint where possible; perceived latency is dominated by TTFT, which streaming + B1 minimizes.
- Streaming already sets `ThinkingConfig(disabled=True)` — keep it; verify the same for the sync path if the chosen model supports thinking.

---

### B10. Infrastructure — stay on CPU (DECIDED)
**Decision (owner-confirmed): the deploy target stays CPU-only. Do NOT add GPU/CUDA requirements, and do NOT downgrade the models to buy speed** — the owner explicitly wants no loss of retrieval quality, and smaller models (`bge-small`, etc.) trade away recall. Keep `BAAI/bge-base-en-v1.5` and `ms-marco-MiniLM-L-6-v2`.

The latency targets are met entirely by the architectural B-series changes (B1 overlap, B2 batching, B3 partial-sort, B5 warmup, B6/B7 dedupe of wasted work) — none of which cost quality. That is the intended path.

CPU tuning that is safe and quality-neutral:
- **Thread count:** `embeddings.py` calls `torch.set_num_threads(8)`. Set this to the deploy box's *physical* core count (not hyperthreads). If the host has 2 cores, `8` oversubscribes and *slows* things down — make it a setting (`TORCH_NUM_THREADS`) and default it sensibly.
- **Only if still too slow after all B-series changes:** convert the cross-encoder to **ONNX + int8** (via `optimum`) — a ~2–4× CPU speedup with negligible quality loss. This is the *last* lever, and it changes no model, just its runtime format. Do not reach for it first.

---

## PART C — Config, verification, rollout

### Config changes (`app/core/config.py`)
Add/adjust:
```python
RERANK_CANDIDATE_POOL: int = 30     # candidates handed to the cross-encoder (replaces the RRF threshold)
RERANK_SCORE_FLOOR: float = 0.02    # min sigmoid(reranker) to keep (post-rerank junk filter); 0 disables
MAX_SUB_QUERIES: int = 3            # cap multi-query fan-out
RERANK_BATCH_SIZE: int = 32
# MIN_RETRIEVAL_THRESHOLD: keep the field for now but STOP using it in hybrid_retriever (A1). Remove later.
```

### Re-ingest procedure (needed only for A5)
Chunk metadata is written at ingest time. After A5:
1. Back up `BACKEND/chroma_db/` (and `BACKEND/chroma_db/bm25_cache/`).
2. Clear the collections (or delete `chroma_db/` to rebuild from scratch).
3. Re-run the corpus ingestion scripts under `BACKEND/scripts/` (e.g. `ingest_corpus.py`, `ingest_sc_judgments.py`, `ingest_schemes.py`) — confirm they tag `tenant_id="global"` (they do).
4. The BM25 index rebuilds automatically on first query, or call `bm25_manager.rebuild_index("global")`.

### Verification protocol (measure, don't assume)
Existing assets to use as ground truth / harness (repo root and `BACKEND/scripts/`):
`retrieval_test_results.json`, `full_rag_test_results.json`, `hard_queries_test.json`, `benchmark_baseline.json`, `scripts/benchmark_corpus.py`, `scripts/benchmark_reranker.py`, `scripts/corpus_health.py`.

1. **Capture baseline BEFORE changes:** run the benchmark/retrieval scripts, save recall@k and latency (embedding/retrieval/generation/total from the `metrics` dict the pipeline already returns).
2. **After each phase:** re-run. Assert:
   - Recall@k on `hard_queries_test.json` **does not drop** (A1–A4 should raise it).
   - Section labels in citations match source text on a spot-check of 10 statute chunks (A5).
   - p50/p95 total latency **drops** (B-series), TTFT drops (B1).
3. **Regression smoke test:** one query through `/api/kanoon` (sync) and one CIVIC query through the streaming endpoint; confirm the response JSON shape is unchanged (`answer`, `citations`, `confidence`, `advanced_metadata`, `metrics`) and citation markers resolve.

### Suggested commit sequencing
- **Phase 1 (correctness, no re-ingest):** A1, A2, A3+A4, plus B2, B3, B6, B7. One PR. Benchmark.
- **Phase 2 (re-ingest):** A5 + re-ingest. Separate PR (has data side-effects).
- **Phase 3 (latency architecture):** B1 (+B1c), B4, B5, B8, B9. Separate PR.
- **Phase 4 (infra):** none — CPU-only is decided (B10). No infra change required.

### Explicitly out of scope / cleanup (do NOT let these expand the diff)
- `_filter_relevant_chunks` (`orchestrator.py:219`) is **dead code** — an LLM relevance filter never wired in. Either delete it or leave it; do **not** add it into the hot path (it would add another blocking LLM call and hurt latency). If retrieval quality is still weak after A1–A5, reconsider it as an *optional, low-confidence-only* step in a later change.
- `hybrid_retriever._bm25_cache` / `_corpus_cache` (line ~23) are unused — safe to delete.
- `nltk.download()` at import time (`bm25_manager.py:15`, `hybrid_retriever.py:10`) makes a network call during module import — breaks offline/air-gapped container starts. Bake punkt/stopwords into the image or move behind the warmup. Low priority.
- `pickle.load` of the BM25 cache (`bm25_manager.py:108`) is fine because the app writes it itself; add a comment so nobody later points it at an uploaded/shared path (deserializing untrusted pickle = RCE).

---

## Quick reference — files touched

| File | Changes |
| :-- | :-- |
| `app/knowledge/hybrid_retriever.py` | A1, A2, A3/A4 (mirror final_score), B3, B7 |
| `app/knowledge/reranker.py` | A3/A4 (sigmoid final_score), B4 (batch_size) |
| `app/knowledge/bm25_manager.py` | B6 (lock, atomic write, negative cache, id_to_index), B7 |
| `app/knowledge/chunking.py` | A5 (Phase 2, re-ingest) |
| `app/ai/orchestrator.py` | A3/A4 (sort by final_score), B1, B1c, B2, B9 |
| `app/main.py` | B5 (warm reranker + BM25) |
| `app/core/config.py` | C (new settings) |

**Start with Phase 1.** A1+A2+A3/A4 together are the accuracy core: today the reranker sees ~⅓ of its intended candidates, scores hybrid chunks with a stray multiplier, then has its ordering thrown away — three small, contained edits fix all of it.
