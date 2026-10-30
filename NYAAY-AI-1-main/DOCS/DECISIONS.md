# NYAAY AI — Architecture Decision Records

> **Version:** 1.0
> **Date:** 2026-06-23
> **Author:** Ansh Darji
> **Status:** Final
> **Total Decisions:** 22

---

## ADR-001: Monolithic Architecture Over Microservices

**Context:** The system has 4 AI features, file processing, auth, and database access. Should these be separate services?

**Options:**
1. **Monolithic FastAPI** — Single server handles everything
2. **Microservices** — Separate services for auth, AI, file processing, etc.

**Decision:** Monolithic FastAPI.

**Rationale:** Single developer, single deployment, single log stream. Microservices add network overhead, distributed debugging, service discovery, and deployment complexity — all unnecessary at MVP scale. A well-structured monolith (with clear module boundaries) is easier to develop, test, and deploy.

**Tradeoffs:** No independent scaling of services. All-or-nothing deployment.

**Reversibility:** Moderate — module boundaries are clean, so extracting services later is feasible.

---

## ADR-002: Firebase Auth Over Custom JWT

**Context:** The application needs authentication with email/password and Google login.

**Options:**
1. **Firebase Authentication** — Google-managed auth service
2. **Custom JWT** — Build auth from scratch (bcrypt + JWT + refresh tokens)
3. **Auth0** — Third-party auth platform

**Decision:** Firebase Authentication.

**Rationale:** Firebase handles password hashing, token signing, token refresh, Google OAuth, and account management. Building this from scratch is 2-3 weeks of work and introduces security risks. Firebase's free tier (10K auths/month) is more than sufficient. The Firebase Web Config is designed to be public — security comes from token verification on the backend.

**Tradeoffs:** Vendor lock-in to Google. No fine-grained auth customization (e.g., custom claims require Firebase Admin SDK).

**Reversibility:** Hard — Auth is deeply integrated. Migration would require re-creating all user accounts.

---

## ADR-003: SQLite Over PostgreSQL

**Context:** The application needs persistent relational storage for users, conversations, messages, documents, uploads, and counter-arguments.

**Options:**
1. **SQLite** — File-based, embedded, zero-config
2. **PostgreSQL** — Server-based, full-featured RDBMS
3. **MySQL** — Server-based, popular for web apps

**Decision:** SQLite.

**Rationale:** Zero configuration, zero cost, zero network latency. The database file lives alongside the application. Perfect for a single-server MVP with < 50 concurrent users. SQLite's WAL mode provides adequate concurrent read/write performance. The schema is PostgreSQL-compatible, making migration straightforward.

**Tradeoffs:** File-level write locking limits concurrent writes. No built-in replication. No remote access.

**Reversibility:** Easy — SQL schema is standard. Migration to PostgreSQL requires only connection string change + minor dialect adjustments.

---

## ADR-004: Raw SQL Over ORM (SQLAlchemy)

**Context:** The database layer needs a data access pattern.

**Options:**
1. **Raw parameterized SQL** — Direct SQL queries with parameter binding
2. **SQLAlchemy ORM** — Object-relational mapping
3. **Tortoise ORM** — Async ORM for FastAPI

**Decision:** Raw parameterized SQL.

**Rationale:** Only 6 tables with straightforward CRUD operations. An ORM adds abstraction overhead, learning curve, and a dependency. Raw SQL is transparent, debuggable, and teaches SQL fundamentals. All queries use parameterized binding (never string interpolation) for SQL injection prevention.

**Tradeoffs:** No automatic migration tools. More boilerplate for complex queries. Must manually handle type mapping.

**Reversibility:** Moderate — Adding SQLAlchemy later requires wrapping existing queries in ORM models, but no schema changes.

---

## ADR-005: ChromaDB Over Pinecone/Weaviate

**Context:** RAG requires a vector database for storing and querying document embeddings.

**Options:**
1. **ChromaDB** — Open-source, embedded, Python-native
2. **Pinecone** — Managed, cloud-hosted vector DB
3. **Weaviate** — Open-source, client-server vector DB
4. **FAISS** — Facebook's similarity search library (no persistence)

**Decision:** ChromaDB.

**Rationale:** ChromaDB runs embedded (same Python process), requires no separate server, has zero network latency for queries, and persists to disk. It integrates natively with LangChain. The free, self-hosted model means no API costs or vendor lock-in. For MVP scale (~10K corpus chunks + per-user documents), ChromaDB is more than sufficient.

**Tradeoffs:** Less scalable than Pinecone for massive datasets. Fewer features than Weaviate. Not suitable for multi-server deployment in embedded mode.

**Reversibility:** Moderate — Vector store interface is abstracted via LangChain. Migration requires re-embedding the corpus.

---

## ADR-006: Embedded ChromaDB Over Client-Server Mode

**Context:** ChromaDB can run embedded (in-process) or as a separate server.

**Options:**
1. **Embedded mode** — ChromaDB runs in the FastAPI process
2. **Client-server mode** — ChromaDB runs as a separate process/container

**Decision:** Embedded mode.

**Rationale:** Zero network latency, zero operational complexity, zero additional processes to manage. Vector queries are sub-millisecond when indexes are in memory. A single-server MVP doesn't need the overhead of a separate vector database server.

**Tradeoffs:** Can't scale vector DB independently. ChromaDB shares memory with FastAPI.

**Reversibility:** Easy — One-line change from `PersistentClient` to `HttpClient`. No data migration needed if using the same storage directory.

---

## ADR-007: Gemini API Over OpenAI GPT-4

**Context:** The application needs an LLM for legal Q&A, document generation, and counter-arguments.

**Options:**
1. **Gemini API** (Google) — Free tier available, good performance
2. **OpenAI GPT-4** — Industry standard, expensive
3. **Claude** (Anthropic) — Strong reasoning, expensive
4. **Open-source LLM** (Llama 3, Mistral) — Self-hosted

**Decision:** Gemini API.

**Rationale:** Gemini offers a generous free tier (~1,500 requests/day), which is sufficient for MVP development and demo. The quality is competitive with GPT-4 for legal text understanding. Single Google ecosystem (Firebase + Gemini) simplifies billing and API key management. Self-hosting an LLM would require GPU resources that aren't available.

**Tradeoffs:** Less community documentation than OpenAI. Google's API may change. Free tier has rate limits.

**Reversibility:** Moderate — Changing LLM requires updating the client wrapper and potentially re-tuning prompts. LangChain abstracts some of this.

---

## ADR-008: Gemini for Both LLM and Embeddings

**Context:** The system needs both text generation and text embedding capabilities.

**Options:**
1. **Gemini for both** — Single provider
2. **Gemini LLM + OpenAI embeddings** — Mixed providers
3. **Gemini LLM + Sentence-Transformers** — Local embeddings

**Decision:** Gemini for both.

**Rationale:** Single API key, single billing, single SDK. Gemini's `embedding-001` model produces quality 768-dim embeddings and is free-tier eligible. No reason to add provider complexity for embeddings. The `RETRIEVAL_DOCUMENT` and `RETRIEVAL_QUERY` task types optimize for asymmetric search.

**Tradeoffs:** If Gemini embedding quality is poor for legal text, we'd need to switch providers and re-embed the entire corpus.

**Reversibility:** Moderate — Changing embedding model requires full corpus re-indexing (~5 min operation).

---

## ADR-009: React Context Over Redux/Zustand

**Context:** The frontend needs global state management for auth and theme.

**Options:**
1. **React Context** — Built-in, zero dependencies
2. **Redux** — Industry standard, boilerplate-heavy
3. **Zustand** — Minimal, modern state manager

**Decision:** React Context.

**Rationale:** Only 2 pieces of global state: auth user and theme. No complex state transitions, no shared state across unrelated component trees, no middleware needs. Context is built-in, zero-dependency, and sufficient for this scale. Adding Redux for 2 contexts would be over-engineering.

**Tradeoffs:** Context re-renders all consumers on state change. Not suitable for high-frequency state updates.

**Reversibility:** Easy — Migrating from Context to Zustand is a 1-hour refactor.

---

## ADR-010: Vite Over Create React App

**Context:** The project needs a React build tool.

**Options:**
1. **Vite** — Modern, fast, actively maintained
2. **Create React App (CRA)** — Legacy, deprecated

**Decision:** Vite.

**Rationale:** CRA is officially deprecated and unmaintained. Vite is the community standard: 10-100× faster builds, instant HMR (Hot Module Replacement), better developer experience, native ES modules, and active maintenance. No reason to use CRA in 2026.

**Tradeoffs:** None — Vite is strictly better.

**Reversibility:** N/A — This is a one-time project setup decision.

---

## ADR-011: Curated Legal Corpus Over Live Scraping

**Context:** Know Your Kanoon needs legal text for RAG grounding.

**Options:**
1. **Curated files** — Manually collected PDFs/text stored in a corpus directory
2. **Indian Kanoon scraping** — Automated web scraping of IndianKanoon.org
3. **Third-party legal API** — Commercial legal data providers
4. **Wikipedia legal articles** — Freely available but unreliable

**Decision:** Curated files.

**Rationale:** Web scraping is legally grey, unreliable (site structure changes), and produces noisy text requiring extensive cleaning. No affordable legal API exists for students. Curated files are controllable, high-quality, and free. The Constitution, BNS, BNSS, and BSA are publicly available government documents. Landmark judgments are available from the Supreme Court website.

**Tradeoffs:** Manual effort to prepare corpus. Corpus doesn't update automatically. Limited to curated content.

**Reversibility:** Easy — Adding more files to the corpus directory and re-running the seed script is trivial.

---

## ADR-012: Per-Document ChromaDB Collections for Uploads

**Context:** User-uploaded documents need to be stored in ChromaDB for RAG queries.

**Options:**
1. **Per-document collections** — Each upload gets its own ChromaDB collection (`doc_{upload_id}`)
2. **Shared collection** — All uploads in one collection with metadata filtering

**Decision:** Per-document collections.

**Rationale:** Structural data isolation — it's impossible to accidentally query another user's document. No metadata filter to get wrong. Query code is simpler (`collection.query()` with no `where` clause). Cleanup is trivial (drop the collection). For a legal platform handling sensitive documents, this security property is worth the scalability tradeoff.

**Tradeoffs:** Many small HNSW indexes. Higher memory overhead per collection. ChromaDB may struggle at 10,000+ collections.

**Reversibility:** Moderate — Migrating to shared collection requires re-inserting all vectors with metadata.

---

## ADR-013: Shared legal_corpus Collection

**Context:** The pre-loaded legal corpus needs a ChromaDB storage strategy.

**Options:**
1. **Single shared collection** — All legal texts in one `legal_corpus` collection
2. **Per-act collections** — Separate collection for each act/judgment

**Decision:** Single shared `legal_corpus` collection.

**Rationale:** Legal queries often span multiple acts (e.g., "What is the punishment for theft?" could involve BNS + case law). A single collection allows cross-act semantic search in a single query. The corpus is read-only after seeding, so there's no data integrity concern. Metadata (source, section, page) enables post-retrieval filtering.

**Tradeoffs:** Larger single index. Can't query a specific act without metadata filtering.

**Reversibility:** Easy — Split into per-act collections by filtering and re-inserting.

---

## ADR-014: Server-Side Disclaimer Injection

**Context:** All AI responses must include a legal disclaimer.

**Options:**
1. **Server-side injection** — Backend appends disclaimer to every AI response before returning
2. **Client-side injection** — Frontend renders disclaimer below AI responses
3. **Prompt-based injection** — System prompt instructs AI to include disclaimer

**Decision:** Server-side injection.

**Rationale:** Server-side ensures the disclaimer cannot be bypassed by a modified frontend or API client. This is a legal compliance measure. The prompt also instructs the AI to include a disclaimer (defense in depth), but the server-side injection is the authoritative source.

**Tradeoffs:** Disclaimer text is duplicated (AI may also generate one). Slightly longer response payloads.

**Reversibility:** Easy — Remove the post-processing step.

---

## ADR-015: REST Synchronous Over WebSocket/SSE

**Context:** Chat features need to deliver AI responses to the frontend.

**Options:**
1. **REST synchronous** — Frontend sends request, waits for full response
2. **WebSocket** — Real-time bidirectional streaming
3. **Server-Sent Events (SSE)** — Unidirectional streaming from server

**Decision:** REST synchronous.

**Rationale:** MVP chat is request-response: user sends a message, waits 3-10 seconds, gets the complete response. There's no real-time requirement (no multi-user chat, no live collaboration). WebSocket/SSE add complexity (connection management, reconnection logic, error handling) for zero user benefit at MVP scale. SSE can be added in Phase 2 for token-by-token streaming.

**Tradeoffs:** User must wait for the full response (3-10s). No streaming progress indicator (only a loading spinner).

**Reversibility:** Easy — Adding SSE is additive (new endpoint alongside existing REST).

---

## ADR-016: Local File Storage Over Cloud Storage

**Context:** Uploaded files and exported documents need persistent storage.

**Options:**
1. **Local filesystem** — Files stored in `uploads/` and `exports/` directories
2. **AWS S3** — Cloud object storage
3. **Firebase Storage** — Google-managed cloud storage
4. **MinIO** — Self-hosted S3-compatible storage

**Decision:** Local filesystem.

**Rationale:** Zero cost, zero configuration, zero network latency. Files stored in organized directories (`uploads/{user_id}/`, `exports/{user_id}/`). Sufficient for single-server MVP. Storage requirements are modest (100 users × 10 uploads × 10MB = 10GB).

**Tradeoffs:** Not scalable for multi-server deployment. No CDN. No automatic backup. No lifecycle policies.

**Reversibility:** Easy — Replace `os.path` operations with `boto3` S3 calls. ~2 day migration.

---

## ADR-017: Separate Prompt Files Over Inline Strings

**Context:** System prompts for each AI feature need to be stored somewhere.

**Options:**
1. **Separate `.txt` files** — One file per prompt in `app/ai/prompts/`
2. **Inline Python strings** — Prompts as multi-line strings in service code
3. **Database storage** — Prompts in a `prompts` table

**Decision:** Separate `.txt` files.

**Rationale:** Prompts are configuration, not code. Separate files produce meaningful Git diffs when prompts change, can be edited by non-engineers, and can be swapped without code changes. They also make prompt versioning and A/B testing easier in Phase 2.

**Tradeoffs:** Slightly more complex file loading. Must handle file-not-found errors.

**Reversibility:** Easy — Copy text into Python strings.

---

## ADR-018: UUID for Public-Facing IDs

**Context:** Entity IDs appear in URLs and API responses.

**Options:**
1. **Auto-increment integers** — Simple, sequential (1, 2, 3...)
2. **UUIDs** — Random, non-sequential
3. **Hybrid** — Integers for internal tables, UUIDs for public entities

**Decision:** Hybrid.

**Rationale:** `users` table uses auto-increment (simple, internal-only, never in URLs). `conversations`, `documents`, `uploads`, `counter_arguments` use UUIDs (exposed in URLs, prevents enumeration attacks). A user can't guess another user's conversation ID by incrementing.

**Tradeoffs:** UUIDs are larger (36 chars vs. ~5 digits). Slightly slower index lookups. More verbose URLs.

**Reversibility:** Hard — Changing ID format requires database migration and URL changes.

---

## ADR-019: 3 DocHub Templates (Reduced from 5)

**Context:** The initial scope included 5 document templates (Legal Notice, Rental Agreement, Affidavit, NDA, Power of Attorney).

**Options:**
1. **5 templates** — Original scope
2. **3 templates** — Legal Notice, Rental Agreement, Affidavit only

**Decision:** 3 templates.

**Rationale:** NDA and Power of Attorney are more complex legal documents requiring extensive clause variations and jurisdiction-specific content. Legal Notice, Rental Agreement, and Affidavit are more commonly needed and simpler to template. 3 templates fully demonstrate the feature. NDA and Power of Attorney are deferred to Phase 2.

**Tradeoffs:** Slightly less impressive feature set. Users who need NDA/PoA must wait for Phase 2.

**Reversibility:** Easy — Add template files and extend the templates config.

---

## ADR-020: 3 User Roles (Removed Researcher)

**Context:** The initial design included 4 roles: Citizen, Student, Researcher, Lawyer.

**Options:**
1. **4 roles** — Citizen, Student, Researcher, Lawyer
2. **3 roles** — Citizen, Student, Lawyer

**Decision:** 3 roles (remove Researcher).

**Rationale:** In the MVP, the Researcher role is functionally identical to Student — same features, same permissions, same UI. Adding a fourth role creates complexity in the role selection UI and role-based logic without providing any distinct functionality. If Researcher-specific features are designed in Phase 2 (e.g., batch analysis, export tools), the role can be re-added.

**Tradeoffs:** Researchers must select "Student" for now. May confuse academic users.

**Reversibility:** Easy — Add 'researcher' to the role CHECK constraint and update UI.

---

## ADR-021: slowapi Rate Limiting

**Context:** API rate limiting is required to prevent abuse and protect Gemini API quotas.

**Options:**
1. **No rate limiting** — Rely on Gemini's own rate limits
2. **slowapi** — Python rate limiting library for FastAPI
3. **Custom middleware** — Build rate limiting from scratch
4. **Nginx rate limiting** — Reverse proxy level

**Decision:** slowapi.

**Rationale:** `slowapi` integrates directly with FastAPI, supports per-user and per-IP limiting, and uses in-memory storage (sufficient for single-server MVP). It's a well-maintained library with minimal configuration. Custom middleware would reinvent the wheel. Nginx rate limiting requires an additional infrastructure component.

**Tradeoffs:** In-memory storage doesn't survive server restarts. Not suitable for multi-server without Redis backend.

**Reversibility:** Easy — Swap slowapi storage backend to Redis for multi-server support.

---

## ADR-022: Tailwind CSS Over Vanilla CSS

**Context:** The frontend needs a styling approach.

**Options:**
1. **Tailwind CSS** — Utility-first CSS framework
2. **Vanilla CSS** — Custom CSS from scratch
3. **Bootstrap** — Component-based CSS framework
4. **Material UI** — React component library

**Decision:** Tailwind CSS.

**Rationale:** Tailwind provides rapid UI development with utility classes, built-in responsive design, dark mode support, and consistent design tokens. It avoids the "naming things" problem of vanilla CSS and the opinionated design of Bootstrap/MUI. The utility-first approach produces smaller final CSS bundles via PurgeCSS. Tailwind is the most popular CSS framework in the React ecosystem.

**Tradeoffs:** Learning curve for utility class syntax. HTML can become verbose. Harder to extract reusable styled components without `@apply`.

**Reversibility:** Hard — CSS framework is deeply integrated into every component. Migration would require rewriting all styles.

---

> **These decisions should be revisited if project constraints change significantly (e.g., multi-developer team, production deployment, enterprise requirements).**
