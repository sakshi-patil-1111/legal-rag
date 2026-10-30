# NYAAY AI 2.0 — Final Technical Debt Report

## Deferred Features & Architectural Trade-Offs

### 1. Semantic Cache Deferred
* **Decision**: We evaluated implementing a semantic cache mapping query embeddings to previously generated JSON responses.
* **Reason for Deferral**: The engineering cost outweighed the expected benefit. Cache invalidation rules (especially concerning shifting legal statutes) and the variability in natural language queries significantly complicated the architecture without a guaranteed high hit rate.
* **Future Recommendation**: Introduce Semantic Caching only if load testing or operational metrics demonstrate severe LLM quota exhaustion.

### 2. Large Scale Synchronous Document Uploads
* **Decision**: Current `upload_chat` relies on synchronous chunking and embedding before returning a success response.
* **Reason for Deferral**: Asynchronous background tasks (e.g., Celery or Redis Queues) would introduce unnecessary infrastructure overhead for an application primarily focused on real-time conversational analysis.
* **Future Recommendation**: If user behavior shifts toward uploading massive multi-hundred-page PDFs, transition the upload endpoint to an asynchronous webhook model.

### 3. Limited Online Learning
* **Decision**: User feedback (Helpful/Not Helpful) is tracked as an analytics metric, but does not autonomously trigger LLM fine-tuning or vector database weight adjustments.
* **Reason for Deferral**: RAG pipelines derive accuracy from the underlying context, not the instruction-following model. Fine-tuning an LLM on user feedback risks introducing bias or hallucination into a deterministic legal architecture.

## Missing Features
* Multi-tenant data segregation is stubbed out via `tenant_id` fields but is heavily defaulted to `"global"`. True SaaS multi-tenancy requires dedicated authorization layers.
