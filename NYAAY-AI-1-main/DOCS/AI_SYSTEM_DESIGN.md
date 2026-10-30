# NYAAY AI System Design

## Retrieval-Augmented Generation (RAG)
NYAAY AI uses an advanced RAG framework to ground all answers in Indian Legal texts.

### Hybrid Retrieval Strategy
- **BM25**: Used for exact keyword matching (Sparse). Cached using Pickle for O(1) load times.
- **ChromaDB**: Used for semantic searching (Dense) powered by Gemini embeddings.
- **Fusion**: Reciprocal Rank Fusion (RRF) combines sparse and dense vectors.

### Prompt Engineering & Security
- **Mitigation**: System prompts employ structured framing and delimiter enforcement to mitigate prompt injection.
- **Guardrails**: Pre-generation and post-generation guardrails validate safety and relevance.
