# NYAAY AI — Executive Review

> **Version:** 1.0
> **Date:** 2026-06-23
> **Author:** Ansh Darji
> **Status:** Final

---

## 1. Overall Project Assessment

**NYAAY AI** is a well-scoped AI-powered legal assistant targeting the Indian judiciary ecosystem. The project demonstrates strong product thinking — it solves a genuine pain point (legal inaccessibility in India), uses modern technologies (RAG, LLMs, Firebase), and is architected for a student-built MVP that can grow.

**Strengths:**
- Clear problem-solution fit — Indian law is genuinely inaccessible to 1.4B people
- Smart technology choices — Gemini (free tier), ChromaDB (embedded), SQLite (zero-config)
- Multiple AI features create demo "wow factor" — Q&A, document analysis, generation, counter-arguments
- Legal domain adds professional weight beyond a generic chatbot
- RAG pipeline with citations shows engineering depth

**Weaknesses to Watch:**
- Legal AI accuracy is inherently risky — hallucinated legal advice could be harmful
- Curated corpus needs manual effort to prepare and maintain
- 4 distinct AI features increase surface area for bugs
- File upload + processing pipeline adds complexity

---

## 2. Scoring Matrix

| Dimension | Score | Justification |
|-----------|:-----:|---------------|
| **MVP Feasibility** | **7/10** | Achievable in 6 weeks by a focused student. Tech stack is well-chosen for solo development. Main risk is RAG pipeline complexity and corpus preparation. No blockers from external dependencies (Firebase and Gemini are free-tier). |
| **Technical Complexity** | **7/10** | Touches 7+ technologies (React, FastAPI, Firebase, SQLite, Gemini, LangChain, ChromaDB). RAG pipeline is non-trivial. File processing adds edge cases. But no microservices, no real-time, no payment — complexity is controlled. |
| **Resume Value** | **9/10** | Exceptional. Demonstrates: full-stack development, AI/LLM integration, RAG architecture, document processing, Firebase auth, database design, REST API design. Legal domain adds uniqueness. Very few student projects combine all these. |
| **Demo Value** | **9/10** | Four distinct AI features create multiple demo moments. Upload a real legal document and chat about it = instant "wow". Generate a legal notice in 10 seconds = tangible output. Counter-arguments show AI reasoning depth. |

---

## 3. Top 10 Risks (Ranked by Severity)

| Rank | Risk | Severity | Impact | Mitigation |
|:----:|------|:--------:|--------|------------|
| 1 | **AI Hallucination in Legal Context** | 🔴 Critical | Users act on fabricated legal citations | RAG grounding, mandatory disclaimers, "I don't know" responses, source attribution |
| 2 | **Gemini API Rate Limits / Downtime** | 🟠 High | All AI features become unusable | Retry with exponential backoff, user-friendly error messages, request queuing |
| 3 | **Legal Corpus Quality** | 🟠 High | Poor RAG retrieval = irrelevant responses | Carefully curate corpus, test retrieval quality, iterate on chunking strategy |
| 4 | **Scope Creep** | 🟠 High | MVP never ships | Strict 3-template DocHub, 3 roles, 6-sprint timeline, cut aggressively |
| 5 | **File Upload Edge Cases** | 🟡 Medium | Corrupt/scanned PDFs, encrypted files crash pipeline | Validate thoroughly, graceful error handling, 10MB + 300 page limits |
| 6 | **RAG Pipeline Complexity** | 🟡 Medium | Chunking/embedding/retrieval issues degrade quality | Start simple (1000 char chunks), test with real legal texts, iterate |
| 7 | **Prompt Injection** | 🟡 Medium | Users manipulate AI to bypass safety constraints | System prompt isolation, input delimiters, output validation |
| 8 | **SQLite Concurrency** | 🟢 Low | Write locks under concurrent users | Acceptable for MVP; PostgreSQL migration path documented |
| 9 | **Firebase Dependency** | 🟢 Low | Auth outage blocks all users | Firebase 99.95% SLA; no practical mitigation needed for MVP |
| 10 | **Legal Liability** | 🟢 Low | User claims reliance on AI advice | Persistent disclaimers, Terms of Service, "not legal advice" on every response |

---

## 4. Recommended Simplifications

| # | Simplification | Time Saved | Impact on Demo |
|---|---------------|:----------:|:--------------:|
| 1 | **Reduce DocHub to 3 templates** (already applied) | ~3 days | Minimal — 3 templates demo the feature fully |
| 2 | **Remove Researcher role** (already applied) | ~1 day | None — role was functionally identical to Student |
| 3 | **Skip dark mode for Sprint 1-5** | ~2 days | Low — add in Sprint 6 polish |
| 4 | **Use simple text editor instead of rich-text for DocHub** | ~2 days | Medium — textarea is sufficient for MVP |
| 5 | **Defer chat search to Sprint 6** | ~1 day | Low — basic list is sufficient |
| 6 | **Use Gemini's built-in PDF understanding** if available | ~3 days | None — could eliminate custom PDF parsing |
| 7 | **Start with 2-3 legal texts in corpus, not full corpus** | ~2 days | Medium — enough for demo, expand later |

---

## 5. Critical Path Analysis

```
Week 1: Foundation + Auth
  ├── Without auth, nothing else works
  └── BLOCKER: Firebase project setup, service account key

Week 2: Dashboard + Know Your Kanoon
  ├── Without Gemini integration, no AI features work
  ├── Without ChromaDB + corpus, no RAG works
  └── BLOCKER: Gemini API key, curated legal corpus files

Week 3: Upload & Chat
  ├── Depends on: RAG pipeline from Week 2
  ├── Depends on: File processing libraries
  └── BLOCKER: None (builds on Week 2 RAG)

Week 4: DocHub
  ├── Depends on: Gemini integration from Week 2
  ├── Depends on: Export libraries (reportlab, python-docx)
  └── BLOCKER: None

Week 5: Counter Arguments + Chat History
  ├── Depends on: RAG pipeline, chat persistence
  └── BLOCKER: None

Week 6: Profile + Polish + Landing Page
  ├── Depends on: All features complete
  └── BLOCKER: None — pure polish
```

**Critical Dependencies:**
1. Firebase project must be created in Week 1
2. Gemini API key must be obtained in Week 1
3. At least 2-3 legal corpus documents must be prepared by Week 2
4. File processing libraries must be tested with real Indian legal PDFs

---

## 6. What Makes This Project Impressive

| Factor | Why It Stands Out |
|--------|------------------|
| **Domain expertise** | Legal AI is a hot, high-value domain — not another todo app or weather app |
| **RAG pipeline** | Shows understanding of modern AI architecture beyond just "calling an API" |
| **Multiple AI features** | Q&A + document analysis + generation + counter-arguments = breadth |
| **Citation system** | Source attribution shows responsible AI engineering |
| **Full-stack depth** | React frontend + FastAPI backend + SQLite + Firebase + Gemini + ChromaDB |
| **Production thinking** | Rate limiting, error handling, security, disclaimers — not just a prototype |

---

## 7. What Could Sink It

| Risk Factor | How to Prevent |
|-------------|---------------|
| **Spending too long on corpus preparation** | Start with Constitution of India + BNS only. Expand later. |
| **Perfectionism on RAG quality** | Ship with "good enough" retrieval. Iterate post-launch. |
| **Overbuilding the landing page** | Landing page is Sprint 6. Don't touch it until core features work. |
| **Fighting PDF parsing edge cases** | Set strict validation (text-based PDFs only). Reject scanned/image PDFs. |
| **Not testing with real legal queries early** | Write 20 test queries in Week 2. Use them throughout development. |

---

## 8. Final Recommendation

**Ship it.** This project is well-scoped, technically impressive, and highly demo-able. The corrections applied (3 roles, 3 templates, curated corpus, rate limiting) have tightened the scope without reducing impact.

**Priority order if time runs short:**
1. Know Your Kanoon (the star feature — demo this first)
2. Upload & Chat (the "wow" feature — upload a real document)
3. Dashboard + Auth (the foundation)
4. Counter Arguments (quick to build on existing RAG)
5. DocHub (nice-to-have for demo, can simplify)
6. Chat History + Profile (lowest priority, can defer)

---

> **This project, if executed well, is a top-tier portfolio piece.**
