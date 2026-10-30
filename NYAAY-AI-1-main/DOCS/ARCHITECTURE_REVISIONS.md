# NYAAY AI — Architecture Revisions

> **Version:** 1.0
> **Date:** 2026-06-23
> **Applies to:** [ARCHITECTURE.md](./ARCHITECTURE.md) v1.0
> **Status:** Final — Changes Identified

---

## Summary

The existing ARCHITECTURE.md contains **10 issues** requiring correction, plus **5 new sections** that must be added. The most significant additions are: Rate Limiting Design, Gemini Failure Handling, Upload Validation Pipeline, Architecture Risks, and Future Scalability.

---

## Part 1: Issues & Corrections

### Issue 1: Template Files Include NDA and Power of Attorney

**Location:** Lines 1285–1289 (Backend folder structure, `prompts/templates/`)
**Severity:** High

```diff
  └── templates/
      ├── affidavit.txt
      ├── rental_agreement.txt
-     ├── nda.txt
      ├── legal_notice.txt
-     └── power_of_attorney.txt
```

---

### Issue 2: TemplateCard Shows ×5

**Location:** Line 450 (Component hierarchy)
**Severity:** Medium

```diff
- │   │   │   │   │       ├── DocHubPage
- │   │   │   │   │       │   └── TemplateCard (×5)
+ │   │   │   │   │       ├── DocHubPage
+ │   │   │   │   │       │   └── TemplateCard (×3)
```

---

### Issue 3: Counter Argument Shows 5 Categories

**Location:** Line 351
**Severity:** Medium

```diff
- The system prompt instructs Gemini to structure output into 5 categories: Opposing Arguments, Legal Rebuttals, Procedural Defenses, Alternative Interpretations, Strategic Perspectives.
+ The system prompt instructs Gemini to structure output into 4 categories: Opposing Viewpoints, Legal Rebuttals, Alternative Interpretations, Strategic Perspectives.
```

**Also update line 458 (component hierarchy):**
```diff
- │   │   │   │   │       │   └── CounterArgumentResults
- │   │   │   │   │       │       └── ArgumentCategory (×5)
+ │   │   │   │   │       │   └── CounterArgumentResults
+ │   │   │   │   │       │       └── ArgumentCategory (×4)
```

---

### Issue 4: Rate Limiting Says "Not Implemented in MVP"

**Location:** Line 1467
**Severity:** High — Rate limiting IS now in MVP scope.

```diff
- | Rate limiting | Not implemented in MVP. Future: add `slowapi` rate limiter. |
+ | Rate limiting | Implemented using `slowapi`. Per-user limits: 20 req/min (chat), 10 req/min (upload, docgen, counter), 5 req/min (auth). See Rate Limiting Design section. |
```

---

### Issue 5: No Upload Page Limit (300 Pages)

**Location:** Section 2.3 (Upload & Chat Flow), around line 256
**Severity:** Medium

**Add to Upload & Chat Key Design Decisions:**
```diff
+ - Maximum page count enforced: 300 pages for PDFs. Page count is checked after file save but before text extraction. Files exceeding 300 pages are rejected and deleted.
```

---

### Issue 6: No Gemini Failure Handling Strategy

**Location:** Section 4.4 (AI Layer), around line 614
**Severity:** High

**Add to `gemini_client.py` description:**
```diff
- | `gemini_client.py` | Wrapper around Gemini Python SDK. Handles API key, model selection, retries, error handling. |
+ | `gemini_client.py` | Wrapper around Gemini Python SDK. Handles API key, model selection, 30s timeout, 3 retries with exponential backoff (1s, 2s, 4s), error categorization (rate limit vs. server error vs. timeout), and user-friendly error messages. See Gemini Failure Handling section. |
```

---

### Issue 7: Legal Corpus Strategy Is Vague

**Location:** Lines 972–973 (RAG Architecture, Document Ingestion)
**Severity:** High

```diff
- **Triggered by:** User file upload (Upload & Chat) OR seed data loading (Know Your Kanoon legal corpus).
+ **Triggered by:** User file upload (Upload & Chat) OR one-time corpus seeding (Know Your Kanoon legal corpus).
+
+ **Legal Corpus Contents:**
+ - Constitution of India (all articles, schedules, amendments)
+ - Bharatiya Nyaya Sanhita (BNS) — replaces IPC
+ - Bharatiya Nagarik Suraksha Sanhita (BNSS) — replaces CrPC
+ - Bharatiya Sakshya Adhiniyam (BSA) — replaces Indian Evidence Act
+ - Selected important Central Acts (e.g., Right to Information Act, Consumer Protection Act, Hindu Marriage Act)
+ - Selected landmark Supreme Court judgments (e.g., Kesavananda Bharati, Maneka Gandhi, Vishaka)
+
+ **Corpus Strategy:** All corpus files are curated PDFs/text files stored in `backend/corpus/` directory. A one-time seed script (`python -m app.scripts.seed_corpus`) processes these files and populates the `legal_corpus` ChromaDB collection. No runtime scraping, no third-party APIs, no live web retrieval.
```

---

### Issue 8: Security Section Too Thin

**Location:** Section 11 (Security Considerations), lines 1442–1477
**Severity:** High

The existing security section covers basics but is missing:
- Detailed prompt injection defense
- RAG poisoning prevention
- File upload magic byte validation
- Logging strategy (what to log vs what NOT to log)

**Resolution:** Refer to the new standalone [SECURITY.md](./SECURITY.md) for comprehensive security design. Add a cross-reference:

```diff
+ > **Note:** For the full security design including prompt injection defense, RAG poisoning prevention, file upload security, and logging strategy, see [SECURITY.md](./SECURITY.md).
```

---

### Issue 9: No Architecture Risks Section

**Location:** Missing — should be added as new Section 13
**Severity:** Medium

See **Part 2, New Section A** below.

---

### Issue 10: No Dedicated Future Scalability Section

**Location:** Section 10.3 has scaling triggers but is incomplete
**Severity:** Medium

See **Part 2, New Section B** below.

---

## Part 2: New Sections to Add

### New Section A: Architecture Risks & Mitigations

Add as **Section 13** (renumber existing sections):

```markdown
## 13. Architecture Risks & Mitigations

### 13.1 Single-Process Bottleneck

**Risk:** The monolithic FastAPI server handles API requests, AI inference orchestration, file processing, and ChromaDB queries in a single process. A slow Gemini API call blocks the worker.

**Mitigation:** FastAPI is async-capable. Use `async/await` for Gemini API calls and file I/O. Uvicorn with 2-4 workers provides basic concurrency. For MVP traffic (< 50 concurrent users), this is sufficient.

**Escalation:** If latency becomes an issue, move AI calls to a background task queue (Celery + Redis).

### 13.2 SQLite Write Contention

**Risk:** SQLite uses file-level locking. Concurrent writes (e.g., two users saving chat messages simultaneously) will queue rather than parallelize.

**Mitigation:** Enable WAL (Write-Ahead Logging) mode for better concurrent read/write performance. For MVP traffic, write contention is negligible.

**Escalation:** Migrate to PostgreSQL when concurrent users exceed ~50.

### 13.3 ChromaDB Memory Usage

**Risk:** Embedded ChromaDB loads vector indexes into memory. With a large legal corpus + many user document collections, memory usage could grow.

**Mitigation:** Legal corpus: ~10K chunks × 768 dims × 4 bytes ≈ 30MB. Per-user documents: ~500 chunks each. At 100 users with 5 uploads each, that's ~500 collections × 500 chunks = 250K chunks ≈ 750MB. Manageable on a 2GB+ server.

**Escalation:** Move to ChromaDB client-server mode or Pinecone when vector count exceeds 1M.

### 13.4 File Storage Growth

**Risk:** Local filesystem stores uploads and exports. No automatic cleanup.

**Mitigation:** 10MB per upload × 100 users × 10 uploads = 10GB. Manageable for MVP. Add a cleanup script for orphaned files.

**Escalation:** Migrate to S3/GCS with lifecycle policies.

### 13.5 Gemini API Cost

**Risk:** As usage grows, Gemini API costs could become significant. Each chat message, document generation, and counter-argument requires an API call.

**Mitigation:** Free tier handles ~1,500 requests/day. Rate limiting (20 req/min per user for chat) prevents abuse. Monitor usage via logging.

**Escalation:** Implement usage quotas per user, add caching for common queries.
```

---

### New Section B: Future Scalability Path

Add as **Section 14** (after Architecture Risks):

```markdown
## 14. Future Scalability Path

### 14.1 Database: SQLite → PostgreSQL

**Trigger:** > 50 concurrent users, or need for advanced queries.

**Migration Path:**
1. Add SQLAlchemy ORM layer (replace raw SQL)
2. Update connection.py to use PostgreSQL connection string
3. Run schema migration via Alembic
4. No application logic changes needed (data access patterns stay the same)

**Effort:** ~2 days
**Risk:** Low — table structures are PostgreSQL-compatible

### 14.2 Vector Store: Embedded ChromaDB → Managed Service

**Trigger:** > 1M vectors, or need for horizontal scaling.

**Migration Path:**
1. Switch ChromaDB to client-server mode (minimal code change)
2. Or migrate to Pinecone/Weaviate (update vector_store.py and retriever.py)
3. Re-embed corpus (one-time operation)

**Effort:** ~3 days
**Risk:** Medium — embedding model change would require full re-indexing

### 14.3 File Storage: Local → Cloud (S3/GCS)

**Trigger:** > 50GB storage, or multi-server deployment.

**Migration Path:**
1. Replace `os.path` file operations with `boto3` (S3) or `google-cloud-storage`
2. Update file_parser.py and exporter modules
3. Migrate existing files with a script

**Effort:** ~2 days
**Risk:** Low

### 14.4 Horizontal Scaling: Single Server → Multi-Instance

**Trigger:** > 100 concurrent users.

**Migration Path:**
1. Dockerize the application
2. Deploy behind a load balancer (Nginx / cloud LB)
3. Move session/state to external stores (PostgreSQL, Redis)
4. ChromaDB must be client-server mode (not embedded)
5. File storage must be cloud-based (not local)

**Effort:** ~1 week
**Risk:** Medium — requires all three migrations above

### 14.5 AI: Synchronous → Streaming

**Trigger:** User experience improvement (faster perceived response).

**Migration Path:**
1. Use Gemini streaming API (`generate_content_stream()`)
2. Backend streams via Server-Sent Events (SSE)
3. Frontend consumes SSE stream and renders tokens incrementally

**Effort:** ~3 days
**Risk:** Low — no architectural changes, additive feature
```

---

### New Section C: Rate Limiting Design

Add to **Section 11** (API Security):

```markdown
### Rate Limiting Design

**Library:** `slowapi` (built on `limits`, integrates with FastAPI)

**Strategy:** Per-user rate limits identified by Firebase UID. Auth endpoints limited by IP.

| Endpoint Group | Limit | Key | Rationale |
|---------------|-------|-----|-----------|
| `/api/auth/*` | 5/min | IP address | Prevent brute force login attempts |
| `/api/chat/*/messages` | 20/min | User ID | Each message triggers a Gemini API call; prevent abuse |
| `/api/upload/files` | 5/min | User ID | File processing is CPU-intensive |
| `/api/upload/*/chat` | 15/min | User ID | Document chat triggers Gemini + RAG |
| `/api/documents/generate` | 10/min | User ID | Document generation triggers Gemini |
| `/api/documents/*/export` | 10/min | User ID | Export is CPU-intensive (PDF generation) |
| `/api/counter/generate` | 10/min | User ID | Counter-args trigger Gemini + RAG |
| `/api/profile/*` | 30/min | User ID | Lightweight DB reads/writes |
| `/api/history/*` | 30/min | User ID | Lightweight DB reads |

**Rate Limit Response:**
- HTTP 429 Too Many Requests
- Response body: `{"error": "rate_limit_exceeded", "message": "Too many requests. Please wait before trying again.", "retry_after_seconds": 60}`
- `Retry-After` header included

**Implementation Notes:**
- Use `slowapi.Limiter` with `get_remote_address` for auth endpoints
- Use custom key function extracting `user_id` from Firebase token for authenticated endpoints
- Store rate limit state in memory (sufficient for single-server MVP)
- Future: Redis-backed rate limiting for multi-server deployment
```

---

### New Section D: Gemini Failure Handling

Add to **Section 4.4** (AI Layer):

```markdown
### Gemini Failure Handling Strategy

#### Timeout Configuration
- **Request timeout:** 30 seconds per Gemini API call
- **Rationale:** Legal responses are complex; Gemini may need up to 20s for detailed answers. 30s gives headroom without making users wait too long.

#### Retry Strategy
| Attempt | Wait | Total Elapsed |
|:-------:|:----:|:-------------:|
| 1st try | 0s | 0s |
| 2nd try | 1s | ~31s |
| 3rd try | 2s | ~63s |
| 4th try | 4s | ~97s |
| Give up | — | ~97s |

- **Max retries:** 3 (4 total attempts)
- **Backoff:** Exponential (1s, 2s, 4s)
- **Retry on:** 429 (rate limit), 500 (server error), 503 (service unavailable), timeout
- **Do NOT retry on:** 400 (bad request), 401 (auth error), 404 (not found)

#### Error Categorization
| Gemini Error | User-Facing Message | HTTP Status |
|-------------|---------------------|:-----------:|
| Rate limit (429) | "Our AI service is temporarily busy. Please try again in a moment." | 503 |
| Server error (500/503) | "Our AI service is temporarily unavailable. Please try again shortly." | 503 |
| Timeout | "The request took too long. Please try a shorter or simpler question." | 504 |
| Invalid response | "We couldn't generate a response. Please rephrase your question." | 502 |
| Content filtered | "Your request could not be processed due to content restrictions." | 422 |
| All retries exhausted | "Our AI service is currently unavailable. Please try again later." | 503 |

#### Graceful Degradation
- If Gemini is down, affected features show an error state (not a crash)
- Non-AI features (dashboard, profile, history listing) continue to work
- Error messages are user-friendly, never expose technical details
- All Gemini failures are logged with request ID, error type, retry count

#### Logging
- Log every Gemini API call: timestamp, feature, input token count, output token count, latency, success/failure
- Do NOT log: full prompt text (contains user data), full response text
- Log error details: error code, error message, retry attempt number
```

---

### New Section E: Upload Validation Pipeline

Add to **Section 4.6** (File Processing Layer):

```markdown
### Upload Validation Pipeline

Every file upload goes through a 5-step validation pipeline before processing:

```
Step 1: Extension Check
  ├── Allowed: .pdf, .docx, .txt
  ├── Check: filename.lower().endswith(('.pdf', '.docx', '.txt'))
  └── Reject: 400 "Unsupported file format. Please upload PDF, DOCX, or TXT."

Step 2: MIME Type Check
  ├── PDF: application/pdf
  ├── DOCX: application/vnd.openxmlformats-officedocument.wordprocessingml.document
  ├── TXT: text/plain
  ├── Check: python-magic library reads file header bytes
  └── Reject: 400 "File content does not match its extension."

Step 3: File Size Check
  ├── Maximum: 10 MB (10,485,760 bytes)
  ├── Check: len(file.read()) or Content-Length header
  └── Reject: 413 "File too large. Maximum size is 10 MB."

Step 4: Page Count Check (PDF only)
  ├── Maximum: 300 pages
  ├── Check: PyPDF2.PdfReader(file).pages length
  └── Reject: 400 "PDF has too many pages. Maximum is 300 pages."

Step 5: Content Extraction Test
  ├── Attempt to extract first page/paragraph of text
  ├── If extraction yields empty/no text → likely scanned/image PDF
  └── Reject: 400 "Unable to extract text. Scanned or image-based PDFs are not supported."
```

**After validation passes:**
1. File saved to `uploads/{user_id}/{upload_id}_{sanitized_filename}`
2. Upload record created in SQLite with status='processing'
3. Text extraction + chunking + embedding begins
4. On success: status updated to 'ready'
5. On failure: status updated to 'error', file kept for debugging
```

---

## Part 3: ChromaDB Design Review

### Approach A: Per-Document Collections (Current Design)

Each uploaded document gets its own ChromaDB collection named `doc_{upload_id}`.

| Aspect | Assessment |
|--------|-----------|
| **Simplicity** | ✅ Simple — query the specific collection, guaranteed isolation |
| **Query complexity** | ✅ Simple — `collection.query()` with no filters needed |
| **Data isolation** | ✅ Perfect — impossible to accidentally query another user's data |
| **Scalability** | ⚠️ ChromaDB creates separate HNSW indexes per collection. At scale (1000+ uploads), this means 1000+ index files. |
| **Cleanup** | ✅ Easy — delete the collection when user deletes upload |
| **Maintenance** | ⚠️ Many small collections can fragment storage |

### Approach B: Shared Collection with Metadata Filtering

All user-uploaded documents stored in a single `user_documents` collection with `upload_id` and `user_id` in metadata. Queries use `where={"upload_id": "xxx"}` filter.

| Aspect | Assessment |
|--------|-----------|
| **Simplicity** | ⚠️ More complex — must always include metadata filters |
| **Query complexity** | ⚠️ Requires `where` clause on every query; filter errors could leak data |
| **Data isolation** | ⚠️ Relies on correct metadata filtering — bugs could cause cross-user data leakage |
| **Scalability** | ✅ Single HNSW index scales better for large vector counts |
| **Cleanup** | ⚠️ Must delete by metadata filter, not just drop collection |
| **Maintenance** | ✅ Single index is easier to manage |

### Recommendation: **Approach A (Per-Document Collections)** for MVP

**Rationale:**
1. **Security over scalability.** Per-document collections make cross-user data leakage structurally impossible, not just logically prevented. For a legal platform handling sensitive documents, this is worth the tradeoff.
2. **Simpler code.** No metadata filters to get wrong. Query the collection, get results.
3. **MVP scale is small.** Even with 100 users × 10 uploads = 1000 collections, ChromaDB handles this fine. The scalability concern only matters at 10,000+ collections.
4. **Easy migration.** If we need to switch to Approach B later (for Pinecone/Weaviate which prefer fewer collections), the migration is straightforward: read all collections → re-insert into shared collection with metadata.

**Keep the current design. No change needed.**

---

## Part 4: Updated Architecture Decisions

Add these to the Architecture Decisions Log (Section 12):

| # | Decision | Options Considered | Chosen | Rationale |
|---|----------|-------------------|--------|-----------|
| 13 | **Curated legal corpus** | Live scraping vs. API-based vs. Curated files | Curated files | No legal API access for students, scraping is legally grey and unreliable, curated files are controllable and high-quality. Constitution + BNS/BNSS/BSA + selected acts + landmark cases provides sufficient MVP coverage. |
| 14 | **slowapi rate limiting** | No rate limiting vs. slowapi vs. custom middleware | slowapi | Simple integration with FastAPI, per-user and per-IP support, in-memory storage sufficient for MVP. Prevents Gemini API abuse. |
| 15 | **3 DocHub templates** | 5 templates vs. 3 templates | 3 templates | NDA and Power of Attorney are complex legal documents that require more template refinement. Legal Notice, Rental Agreement, and Affidavit are more commonly needed and simpler to template. Reduces scope without reducing demo value. Move NDA and PoA to Phase 2. |
| 16 | **3 user roles** | 4 roles (incl. Researcher) vs. 3 roles | 3 roles (Citizen, Student, Lawyer) | Researcher role was functionally identical to Student in MVP — same features, same permissions. Adding it created unnecessary complexity in role selection UI and role-based logic. Can be re-added in Phase 2 if distinct features are designed. |

---

> These revisions have been identified but **not yet applied** to the original ARCHITECTURE.md. Apply them before beginning Sprint 1 implementation.
