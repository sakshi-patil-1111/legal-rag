# NYAAY AI — RAG Architecture

> **Version:** 1.0
> **Date:** 2026-06-23
> **Author:** Ansh Darji
> **Status:** Final
> **References:** [ARCHITECTURE.md](./ARCHITECTURE.md), [API_SPEC.md](./API_SPEC.md)

---

## 1. Legal Corpus Strategy

### 1.1 What's Included

| Category | Documents | Estimated Size | Priority |
|----------|-----------|:-------------:|:--------:|
| **Constitution** | Constitution of India (all 395+ articles, 12 schedules, amendments) | ~500 pages | P0 |
| **Criminal Law** | Bharatiya Nyaya Sanhita (BNS) — replaces IPC | ~300 pages | P0 |
| **Criminal Procedure** | Bharatiya Nagarik Suraksha Sanhita (BNSS) — replaces CrPC | ~400 pages | P0 |
| **Evidence Law** | Bharatiya Sakshya Adhiniyam (BSA) — replaces Indian Evidence Act | ~150 pages | P0 |
| **Key Central Acts** | Right to Information Act, Consumer Protection Act, Hindu Marriage Act, IT Act 2000, POCSO Act (5-8 acts) | ~500 pages | P1 |
| **Landmark Judgments** | 10-15 landmark Supreme Court judgments (Kesavananda Bharati, Maneka Gandhi, Vishaka, Navtej Singh Johar, etc.) | ~200 pages | P1 |

**Total estimated corpus size:** ~2,000 pages → ~6,000-8,000 chunks

### 1.2 Source Format

```
backend/
├── corpus/
│   ├── constitution/
│   │   └── constitution_of_india.pdf
│   ├── criminal_law/
│   │   ├── bns_2023.pdf
│   │   ├── bnss_2023.pdf
│   │   └── bsa_2023.pdf
│   ├── central_acts/
│   │   ├── rti_act_2005.pdf
│   │   ├── consumer_protection_2019.pdf
│   │   └── ...
│   └── landmark_judgments/
│       ├── kesavananda_bharati_1973.pdf
│       ├── maneka_gandhi_1978.pdf
│       └── ...
```

All files are manually curated PDFs or text files. **No runtime scraping. No third-party legal APIs. No Indian Kanoon integration. No live web retrieval.**

### 1.3 Ingestion Workflow

```
python -m app.scripts.seed_corpus

1. Scan backend/corpus/ directory recursively
2. For each file:
   a. Extract text (PyPDFLoader / TextLoader)
   b. Pre-process (whitespace, Unicode normalization)
   c. Split into chunks (RecursiveCharacterTextSplitter)
   d. Enrich metadata (source name, category, page number, section)
   e. Embed chunks (Gemini models/embedding-001, task=RETRIEVAL_DOCUMENT)
   f. Store in ChromaDB 'legal_corpus' collection
3. Report: total files processed, total chunks created, total time
4. Mark collection as seeded (write a marker file or DB flag)
```

**Idempotency:** The seed script checks if the `legal_corpus` collection already exists. If it does, it can either skip (fast) or delete-and-recreate (full reseed).

---

## 2. Document Ingestion Pipeline

### 2.1 Upload Validation

```
Step 1: Extension Check
  ├── Allowed: .pdf, .docx, .txt
  └── Reject → 400 "Unsupported file format"

Step 2: MIME Type Check (python-magic)
  ├── PDF: application/pdf
  ├── DOCX: application/vnd.openxmlformats-officedocument.wordprocessingml.document
  ├── TXT: text/plain
  └── Reject → 400 "File content does not match its extension"

Step 3: File Size Check
  ├── Maximum: 10 MB (10,485,760 bytes)
  └── Reject → 413 "File too large"

Step 4: Page Count Check (PDF only)
  ├── Maximum: 300 pages
  └── Reject → 400 "PDF has too many pages"

Step 5: Content Extraction Test
  ├── Extract first page/paragraph
  ├── If empty text → scanned/image PDF
  └── Reject → 400 "Unable to extract text"
```

### 2.2 Text Extraction

| File Type | Library | Method | Output |
|-----------|---------|--------|--------|
| PDF | `PyPDFLoader` (LangChain) | Page-by-page extraction | List of Document objects with page metadata |
| DOCX | `Docx2txtLoader` (LangChain) | Full text extraction | Single Document object |
| TXT | `TextLoader` (LangChain) | Raw text read | Single Document object |

### 2.3 Pre-processing

```python
def preprocess(text: str) -> str:
    # 1. Normalize Unicode (NFKC normalization)
    text = unicodedata.normalize('NFKC', text)

    # 2. Replace multiple whitespace with single space (preserve newlines)
    text = re.sub(r'[^\S\n]+', ' ', text)

    # 3. Replace 3+ newlines with 2 (preserve paragraph boundaries)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # 4. Strip leading/trailing whitespace
    text = text.strip()

    return text
```

### 2.4 Error Handling

| Error Case | Detection | Response |
|-----------|-----------|----------|
| Corrupt PDF | PyPDF2 raises exception | Set upload status='error', return 500 |
| Password-protected PDF | PyPDF2.errors.PdfReadError | Reject with 400 "Encrypted PDFs are not supported" |
| Empty document | Extracted text length == 0 | Reject with 400 "No text content found" |
| Encoding error (TXT) | UnicodeDecodeError | Try utf-8, latin-1 fallback; reject if both fail |
| Gemini embedding failure | API error during embedding | Set upload status='error', allow retry |

---

## 3. Chunking Strategy

### 3.1 Configuration

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ". ", " ", ""],
    length_function=len,
)
```

### 3.2 Why These Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `chunk_size` | 1000 chars | ~200-250 words ≈ 1-2 legal paragraphs. Large enough to capture a complete legal clause or section, small enough for precise retrieval. |
| `chunk_overlap` | 200 chars | Prevents loss of context at chunk boundaries. A sentence at the end of one chunk appears at the start of the next. |
| `separators` | `["\n\n", "\n", ". ", " ", ""]` | Splits on natural boundaries: paragraphs first, then lines, then sentences, then words. Legal texts are structured with clear paragraphs, making `\n\n` the most common split point. |

### 3.3 Legal Text Considerations

Legal documents have specific structure patterns:

```
Section 302. Murder.—
  Whoever commits murder shall be punished with death, or imprisonment
  for life, and shall also be liable to fine.

  Explanation.—...
```

The chunking strategy preserves:
- **Section headers** (usually preceded by `\n\n`)
- **Explanations and provisos** (indented paragraphs)
- **Cross-references** ("See Section 299")

### 3.4 Metadata Preservation

Each chunk carries metadata from extraction:

```python
{
    "source": "Bharatiya Nyaya Sanhita",    # Document/Act name
    "category": "criminal_law",              # Corpus category
    "page": 42,                              # Page number (PDF only)
    "section": "302",                        # Extracted if detectable
    "chapter": "XVI",                        # Extracted if detectable
    "chunk_index": 7,                        # Position in document
    "file_name": "bns_2023.pdf",             # Original filename
    "total_chunks": 450                      # Total chunks in document
}
```

**Section/Chapter extraction:** Best-effort regex extraction from chunk text. Pattern: `Section\s+(\d+[A-Z]?)` and `Chapter\s+([IVXLCDM]+|\d+)`. Not perfect, but sufficient for citation metadata.

---

## 4. Embedding Pipeline

### 4.1 Model Configuration

| Property | Value |
|----------|-------|
| **Model** | `models/embedding-001` (Gemini) |
| **Dimensions** | 768 |
| **Task Type (Indexing)** | `RETRIEVAL_DOCUMENT` |
| **Task Type (Querying)** | `RETRIEVAL_QUERY` |

**Why asymmetric task types:** `RETRIEVAL_DOCUMENT` optimizes embeddings for long passages (chunks). `RETRIEVAL_QUERY` optimizes for short queries. This asymmetric approach produces better similarity scores than using the same task type for both.

### 4.2 Batch Embedding (Corpus Ingestion)

```python
# Pseudo-code for batch embedding
BATCH_SIZE = 100  # Gemini embedding API supports batching

for i in range(0, len(chunks), BATCH_SIZE):
    batch = chunks[i:i+BATCH_SIZE]
    texts = [chunk.page_content for chunk in batch]

    embeddings = gemini_embed(
        texts=texts,
        model="models/embedding-001",
        task_type="RETRIEVAL_DOCUMENT"
    )

    # Store in ChromaDB
    collection.add(
        ids=[f"chunk_{uuid4()}" for _ in batch],
        embeddings=embeddings,
        documents=texts,
        metadatas=[chunk.metadata for chunk in batch]
    )

    # Rate limit: pause 100ms between batches
    time.sleep(0.1)
```

### 4.3 Error Handling & Retry

| Scenario | Action |
|----------|--------|
| Gemini 429 (rate limit) | Wait 60s, retry. Use exponential backoff for corpus seeding. |
| Gemini 500 (server error) | Retry 3×, backoff 1s/2s/4s |
| Gemini timeout | Retry 3× with 30s timeout |
| Partial batch failure | Log failed chunks, continue with remaining. Report failures at end. |
| All retries failed | Skip chunk, log error, continue. User documents: set status='error'. |

### 4.4 Embedding Latency Estimates

| Operation | Estimated Latency |
|-----------|:----------------:|
| Single text embedding | ~100-200ms |
| Batch of 100 texts | ~500-1000ms |
| Full legal corpus (~8,000 chunks) | ~2-5 minutes |
| Single user document (~500 chunks) | ~30-60 seconds |

---

## 5. ChromaDB Collection Design

### 5.1 Collection Architecture

```
ChromaDB (persistent mode: backend/chroma_db/)
├── legal_corpus              ← Shared, read-only after seeding
│   ├── ~8,000 chunks
│   └── Used by: Know Your Kanoon, Counter Arguments
│
├── doc_{upload_id_1}         ← User A's uploaded document
│   ├── ~200 chunks
│   └── Used by: Upload & Chat (scoped to this document)
│
├── doc_{upload_id_2}         ← User A's another document
│   ├── ~500 chunks
│   └── Used by: Upload & Chat (scoped to this document)
│
└── doc_{upload_id_3}         ← User B's uploaded document
    ├── ~100 chunks
    └── Used by: Upload & Chat (scoped to this document)
```

### 5.2 Design Decision: Per-Document Collections vs. Shared Collection

| Criterion | Per-Document Collections | Shared Collection + Metadata |
|-----------|:------------------------:|:----------------------------:|
| **Data Isolation** | ✅ Perfect — structurally impossible to leak | ⚠️ Relies on correct `where` clause |
| **Query Simplicity** | ✅ `collection.query(query)` — no filters | ⚠️ Must add `where={"upload_id": id}` always |
| **Security Risk** | ✅ Zero cross-user risk | ⚠️ Bug in filter = data leakage |
| **Cleanup** | ✅ Drop collection | ⚠️ Delete by metadata filter |
| **Scalability** | ⚠️ Many small HNSW indexes | ✅ Single large index |
| **Memory** | ⚠️ Each index has fixed overhead | ✅ One index, lower overhead |
| **MVP Fit** | ✅ Simpler, safer | ⚠️ More code, more risk |

**Decision: Per-Document Collections.**

For a legal platform handling sensitive documents, structural data isolation is worth the scalability tradeoff. At MVP scale (< 1000 collections), ChromaDB handles per-document collections well.

### 5.3 Collection Schema

```python
# Legal Corpus Collection
{
    "id": "chunk_{uuid}",
    "embedding": [0.123, -0.456, ...],     # 768-dim
    "document": "Section 302. Murder.—...", # chunk text
    "metadata": {
        "source": "Bharatiya Nyaya Sanhita",
        "category": "criminal_law",
        "page": 42,
        "section": "302",
        "chapter": "XVI",
        "chunk_index": 7,
        "file_name": "bns_2023.pdf"
    }
}

# User Document Collection
{
    "id": "chunk_{uuid}",
    "embedding": [0.789, -0.012, ...],     # 768-dim
    "document": "The tenant shall pay...",  # chunk text
    "metadata": {
        "source": "rental_agreement.pdf",
        "page": 3,
        "chunk_index": 12,
        "file_name": "rental_agreement.pdf",
        "user_id": "user_abc123"
    }
}
```

### 5.4 Storage Configuration

```python
import chromadb

# Persistent storage in backend/chroma_db/
client = chromadb.PersistentClient(path="./chroma_db")

# Create legal corpus collection (once)
legal_corpus = client.get_or_create_collection(
    name="legal_corpus",
    metadata={"hnsw:space": "cosine"}
)

# Create per-document collection (on upload)
doc_collection = client.get_or_create_collection(
    name=f"doc_{upload_id}",
    metadata={"hnsw:space": "cosine"}
)
```

---

## 6. Retrieval Pipeline

### 6.1 Query Flow

```
User Query: "What does Section 302 of BNS say about murder?"
       │
       ▼
┌─────────────────────┐
│ 1. Embed Query       │
│    model: embedding-001
│    task: RETRIEVAL_QUERY
│    → query_vector (768-dim)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 2. Select Collection │
│    Know Your Kanoon → legal_corpus
│    Upload & Chat    → doc_{upload_id}
│    Counter Args     → legal_corpus
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 3. Similarity Search │
│    collection.query(
│      query_embeddings=[query_vector],
│      n_results=5,
│      include=["documents", "metadatas", "distances"]
│    )
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 4. Relevance Filter  │
│    Discard if distance > 0.8
│    (cosine distance; lower = more similar)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 5. Assemble Context  │
│    Format each chunk with source metadata
│    Join with separator
│    Return context string + metadata list
└─────────────────────┘
```

### 6.2 Retrieval Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `n_results` | 5 | 5 chunks × 1000 chars = ~5000 chars of context. Sufficient for detailed answers without overwhelming Gemini's context window. |
| Distance metric | Cosine (ChromaDB default) | Standard for text embeddings. Range 0-2 (0 = identical, 2 = opposite). |
| Relevance threshold | 0.8 | Chunks with distance > 0.8 are unlikely to be relevant. Prevents injecting noise into the prompt. Tunable based on testing. |

### 6.3 Context Assembly

```python
def assemble_context(results: dict) -> tuple[str, list[dict]]:
    """Convert ChromaDB results into context string and citation metadata."""
    context_parts = []
    citations = []

    for doc, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        # Skip irrelevant chunks
        if distance > 0.8:
            continue

        # Build context part with source info
        source_label = f"[Source: {metadata.get('source', 'Unknown')}"
        if metadata.get('section'):
            source_label += f", Section: {metadata['section']}"
        if metadata.get('page'):
            source_label += f", Page: {metadata['page']}"
        source_label += "]"

        context_parts.append(f"{source_label}\n{doc}")
        citations.append(metadata)

    context = "\n---\n".join(context_parts)
    return context, citations
```

### 6.4 Multi-Collection Query Routing

| Feature | Collection Queried | Rationale |
|---------|-------------------|-----------|
| **Know Your Kanoon** | `legal_corpus` | User asks general legal questions → search curated legal texts |
| **Upload & Chat** | `doc_{upload_id}` | User asks about their document → search only that document's chunks |
| **Counter Arguments** | `legal_corpus` | Counter-args need legal grounding → search legal texts for relevant laws/precedents |

---

## 7. Citation Pipeline

### 7.1 Citation Flow

```
1. RAG retrieves chunks with metadata
   → [{"source": "BNS", "section": "302", "page": 42}, ...]

2. System prompt instructs Gemini:
   "Reference your sources using [Source: X, Section: Y] format.
    Only cite sources present in the provided context.
    Do NOT fabricate citations."

3. Gemini generates response with inline citations:
   "Section 302 of BNS [Source: BNS, Section: 302] defines murder as..."

4. Backend post-processing:
   a. Parse response for [Source: ...] patterns
   b. Match parsed citations to metadata from retrieved chunks
   c. Build structured citations array
   d. Append disclaimer to response
   e. Store citations as JSON in messages.citations column

5. Frontend renders:
   a. Response text with clickable citation markers
   b. Citation panel showing source details
   c. Disclaimer banner at bottom
```

### 7.2 Citation JSON Structure

```json
[
  {
    "source": "Bharatiya Nyaya Sanhita",
    "section": "302",
    "page": 42,
    "relevance": "direct",
    "chunk_preview": "Section 302. Murder.— Whoever commits..."
  },
  {
    "source": "Kesavananda Bharati v. State of Kerala",
    "year": "1973",
    "page": null,
    "relevance": "supporting",
    "chunk_preview": "The basic structure doctrine..."
  }
]
```

### 7.3 Citation Rendering (Frontend)

```
AI Response Text:
  "Section 302 of BNS [1] defines murder as the intentional
   causing of death. The Supreme Court in State v. Ram [2]
   established that..."

Citation Panel (sidebar or footer):
  [1] Bharatiya Nyaya Sanhita, Section 302, Page 42
  [2] State v. Ram, 2019 SCC 456, Page 12
```

---

## 8. Hallucination Prevention

### 8.1 Strategy Overview

```
┌─────────────────────────────────────────┐
│         HALLUCINATION PREVENTION         │
│                                          │
│  Layer 1: RAG Grounding                 │
│    ├── Only provide retrieved context    │
│    └── Instruct: "Answer ONLY from      │
│         provided context"               │
│                                          │
│  Layer 2: System Prompt Constraints     │
│    ├── "Do NOT fabricate citations"      │
│    ├── "If context insufficient,         │
│    │    say 'I don't have information'"  │
│    └── "Clearly separate fact from      │
│         interpretation"                  │
│                                          │
│  Layer 3: Post-Processing               │
│    ├── Validate citations against        │
│    │    retrieved chunks                 │
│    └── Append mandatory disclaimer      │
│                                          │
│  Layer 4: User Communication            │
│    ├── Disclaimer on every response     │
│    ├── Citation panel for verification  │
│    └── "Not legal advice" banner        │
└─────────────────────────────────────────┘
```

### 8.2 "I Don't Know" Response

When no relevant context is found (all chunks have distance > 0.8):

```json
{
  "content": "I don't have sufficient information in my legal knowledge base to answer this question accurately. This could be because:\n\n1. The topic may not be covered in the current legal corpus\n2. The question may require more specific details\n3. The legal area may be outside the scope of currently indexed documents\n\nI recommend consulting a qualified legal professional for this query.\n\n⚖️ *This is AI-generated information, not legal advice.*",
  "citations": []
}
```

### 8.3 Confidence-Aware Output

The system prompt instructs Gemini to use hedging language when context is limited:

- **Strong context (3+ relevant chunks):** "Section 302 of BNS states that..."
- **Moderate context (1-2 relevant chunks):** "Based on available information, Section 302 appears to..."
- **Weak context (borderline relevance):** "The available legal texts suggest... however, I recommend verifying this with a legal professional."

---

## 9. Prompt Engineering

### 9.1 System Prompt Design

#### Know Your Kanoon System Prompt

```
You are NYAAY AI, an AI legal assistant specializing in Indian law.

Your role is to help users understand Indian legal concepts, laws, and procedures
based ONLY on the provided legal context.

RULES:
1. ONLY answer based on the provided legal context. Do NOT use external knowledge.
2. If the context does not contain relevant information, say "I don't have
   sufficient information in my legal knowledge base to answer this."
3. Always cite your sources using [Source: X, Section: Y] format.
4. Do NOT fabricate citations or legal provisions.
5. Clearly distinguish between:
   - What the law states (fact)
   - Your interpretation or explanation (analysis)
6. Use simple, clear language. Avoid excessive legal jargon unless the user
   appears legally trained.
7. When explaining complex legal concepts, use examples.
8. Always end with: "⚖️ This is AI-generated information, not legal advice.
   Consult a qualified lawyer for legal decisions."

CONTEXT:
{retrieved_context}

CONVERSATION HISTORY:
{last_n_messages}

USER QUESTION:
{user_message}
```

#### Upload & Chat System Prompt

```
You are NYAAY AI, analyzing a document uploaded by the user.

The document is: "{document_name}"

Your role is to help the user understand the contents of this document based
ONLY on the document's text provided in the context.

RULES:
1. ONLY answer based on the provided document context.
2. Reference specific sections, clauses, or pages when answering.
3. If the question is not answerable from the document, say so clearly.
4. Do NOT add information not present in the document.
5. Use [Page: X] format when citing specific locations.

CONTEXT FROM DOCUMENT:
{retrieved_context}

CONVERSATION HISTORY:
{last_n_messages}

USER QUESTION:
{user_message}
```

#### Counter Argument System Prompt

```
You are NYAAY AI, a legal argument analyst.

Given a legal argument or position, generate counter-arguments organized into
EXACTLY 4 categories:

1. **Opposing Viewpoints** — Direct challenges to the argument's core thesis
2. **Legal Rebuttals** — Counter-arguments grounded in specific laws, sections,
   or case precedents from the provided context
3. **Alternative Interpretations** — Different ways to interpret the same
   legal provisions or facts
4. **Strategic Perspectives** — Practical or strategic considerations that
   weaken the argument

RULES:
1. Ground your counter-arguments in the provided legal context when possible.
2. Cite specific laws, sections, or cases using [Source: X, Section: Y].
3. For each counter-argument, rate its strength as: strong, moderate, or advisory.
4. Provide 2-3 counter-arguments per category.
5. Do NOT fabricate case names or legal provisions.
6. End with a disclaimer.

LEGAL CONTEXT:
{retrieved_context}

ARGUMENT TO COUNTER:
{user_argument}
```

#### DocHub System Prompt

```
You are NYAAY AI, a legal document drafter.

Generate a professional {template_type} using the provided field values.

RULES:
1. Follow standard Indian legal document format.
2. Include all legally required sections and clauses.
3. Use formal legal language appropriate for Indian courts.
4. Include proper date and location formatting.
5. Do NOT add fabricated details — use only provided field values.
6. Include signature blocks where appropriate.

TEMPLATE: {template_type}
FIELDS:
{field_values_json}
```

### 9.2 Multi-Turn History Management

```python
# Include last N messages for conversation context
MAX_HISTORY_MESSAGES = 10  # 5 user + 5 assistant messages

def build_conversation_history(messages: list) -> str:
    """Format recent messages for prompt injection."""
    recent = messages[-MAX_HISTORY_MESSAGES:]
    history = []
    for msg in recent:
        role = "User" if msg.role == "user" else "Assistant"
        history.append(f"{role}: {msg.content[:500]}")  # Truncate long messages
    return "\n".join(history)
```

### 9.3 Token Budget Management

| Component | Estimated Tokens | Budget Allocation |
|-----------|:----------------:|:-----------------:|
| System prompt | ~300 tokens | Fixed |
| Retrieved context (5 chunks × 1000 chars) | ~1,500 tokens | Variable |
| Conversation history (10 messages × 500 chars) | ~1,500 tokens | Variable |
| User message | ~100-500 tokens | Variable |
| **Total input** | **~3,500-4,000 tokens** | — |
| AI response | ~500-2,000 tokens | — |
| **Total per request** | **~4,000-6,000 tokens** | Well within Gemini's 32K context |

---

## 10. Performance Considerations

### 10.1 Latency Estimates

| Operation | Estimated Latency | Notes |
|-----------|:-----------------:|-------|
| Query embedding | 100-200ms | Single API call to Gemini |
| ChromaDB similarity search | 10-50ms | In-memory HNSW index |
| Context assembly | < 5ms | String operations |
| Gemini response generation | 2-10s | Depends on response length |
| **Total end-to-end** | **~3-11s** | Dominated by Gemini generation |

### 10.2 Corpus Size Estimates

| Corpus Component | Estimated Chunks |
|-----------------|:----------------:|
| Constitution of India | ~1,500 |
| BNS | ~900 |
| BNSS | ~1,200 |
| BSA | ~450 |
| 5-8 Central Acts | ~1,500 |
| 10-15 Landmark Judgments | ~600 |
| **Total** | **~6,000-8,000** |

**ChromaDB memory usage:** ~8,000 chunks × 768 dims × 4 bytes ≈ **~24 MB** for vectors, plus metadata and text storage ≈ **~50 MB total**. Negligible for any modern server.

### 10.3 Optimization Strategies

| Strategy | Implementation | Impact |
|----------|---------------|--------|
| **Batch embedding** | Process corpus in batches of 100 | Reduces API calls by 100× during seeding |
| **Embedding cache** | Cache query embeddings for repeated queries | Saves ~150ms per repeated query |
| **Connection pooling** | Reuse ChromaDB client instance | Eliminates connection overhead |
| **Async Gemini calls** | Use `async` for Gemini API calls | Prevents blocking the event loop |
| **Chunk deduplication** | Skip duplicate chunks during ingestion | Reduces corpus size |

---

> **Next Step:** Upon approval, the legal corpus files should be collected and the seed script should be implemented in Sprint 2 (Dashboard & Know Your Kanoon).
