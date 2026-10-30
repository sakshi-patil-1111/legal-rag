# NYAAY AI — Product Requirements Document (PRD)

> **Version:** 1.0  
> **Date:** 2026-06-23  
> **Author:** Ansh Darji  
> **Status:** Draft — Awaiting Approval

---

## 1. Executive Summary

**NYAAY AI** is an AI-powered legal assistant designed for the Indian judiciary ecosystem. It empowers citizens, students, researchers, and legal professionals to navigate Indian law through natural-language interactions, document analysis, legal document generation, and argumentative reasoning — all without requiring deep legal expertise.

The MVP focuses on delivering six core AI features behind a clean, modern web interface with Firebase-based authentication and a FastAPI backend.

---

## 2. Problem Statement

### The Problem

Indian law is vast — spanning 1,300+ Central Acts, 40,000+ State Acts, and millions of case judgments. Accessing, understanding, and applying this knowledge is prohibitively complex for:

- **Citizens** who cannot afford legal counsel for basic legal questions.
- **Students** who need structured explanations of legal concepts and case law.
- **Researchers** who need efficient search and synthesis across legal corpora.
- **Lawyers** who spend disproportionate time on document drafting and argument preparation.

### Why Now

- Large Language Models (Gemini) have reached sufficient capability for legal reasoning with proper grounding.
- RAG (Retrieval-Augmented Generation) enables factual, citation-backed responses.
- The Indian government's push toward digitization (e-Courts, Indian Kanoon) has made legal data increasingly accessible.

---

## 3. Vision & Goals

### Vision

Make Indian law accessible, understandable, and actionable for everyone — through AI that explains, drafts, and reasons, while always being transparent about its limitations.

### MVP Goals

| # | Goal | Success Metric |
|---|------|---------------|
| 1 | Allow users to ask legal questions and receive grounded, cited answers | Users can complete a legal Q&A session end-to-end |
| 2 | Allow users to upload legal documents and interact with them via chat | PDF/DOCX/TXT upload → chat within 10 seconds |
| 3 | Allow users to generate legal documents from templates | At least 5 templates available and exportable |
| 4 | Allow users to explore counter-arguments for legal positions | Counter-arguments generated with cited reasoning |
| 5 | Provide a clean, intuitive user experience | All core features accessible within 2 clicks from dashboard |
| 6 | Implement secure authentication and user management | Firebase Auth with email/password and Google login |

### Non-Goals (MVP)

- Payment/subscription system
- Multi-language support (Hindi, etc.) — future phase
- Mobile native apps (iOS/Android)
- Real-time collaboration
- Lawyer marketplace or matchmaking
- Court case tracking / e-Filing integration
- Admin panel

---

## 4. Target Users & Personas

### Persona 1: Citizen (Ravi, 34, Small Business Owner)

- **Need:** Understand a rental agreement clause; know his tenant rights.
- **Pain:** Cannot afford ₹5,000+ for a lawyer for a simple question.
- **NYAAY AI Use:** Uploads rental agreement → asks "What are the termination clauses?" → gets plain-language explanation.

### Persona 2: Student (Priya, 22, Law Student)

- **Need:** Research case law on Article 21 (Right to Life) for a moot court.
- **Pain:** Spending hours searching Indian Kanoon and manually reading judgments.
- **NYAAY AI Use:** Uses "Know Your Kanoon" → asks "Landmark cases on Article 21 and euthanasia" → receives structured case summaries with citations.

### Persona 3: Researcher (Dr. Mehra, 45, Legal Academic)

- **Need:** Analyze patterns in Supreme Court judgments on environmental law.
- **Pain:** Manual reading of hundreds of judgments.
- **NYAAY AI Use:** Uploads a batch of judgments → asks for summarization and clause extraction → exports findings.

### Persona 4: Lawyer (Adv. Sharma, 38, Practicing Advocate)

- **Need:** Draft a legal notice for a client and prepare counter-arguments for an ongoing case.
- **Pain:** Repetitive drafting and extensive manual research.
- **NYAAY AI Use:** Uses DocHub to generate a legal notice → uses Counter Argument Generator to prepare rebuttals.

---

## 5. Feature Requirements

### 5.1 Landing Page

**Priority:** P0 (Must Have)

| Requirement | Details |
|-------------|---------|
| Hero Section | Tagline, subtitle, primary CTA ("Get Started"), secondary CTA ("Learn More") |
| Product Overview | Brief explanation of what NYAAY AI does, with visual/icon support |
| Feature Showcase | Cards or sections highlighting each core feature (Know Your Kanoon, Upload & Chat, DocHub, Counter Arguments) |
| Social Proof | Placeholder section for testimonials / stats (can be dummy data for MVP) |
| Footer | Links to About, Contact, Terms of Service, Privacy Policy (placeholder pages for MVP) |
| Navigation | Responsive navbar with Logo, feature links, Login, Signup buttons |

**Acceptance Criteria:**
- Page loads in under 3 seconds.
- Fully responsive (mobile, tablet, desktop).
- CTA buttons navigate to signup/login.

---

### 5.2 Authentication

**Priority:** P0 (Must Have)

| Requirement | Details |
|-------------|---------|
| Provider | Firebase Authentication |
| Methods | Email/Password signup + login, Google OAuth login |
| User Roles | Citizen, Student, Researcher, Lawyer (selected at signup) |
| Session Management | Firebase ID tokens verified on backend via Firebase Admin SDK |
| Protected Routes | All routes except Landing Page and Auth pages require authentication |
| Logout | Clear Firebase session, redirect to Landing Page |

**Acceptance Criteria:**
- Users can register with email/password and select a role.
- Users can sign in with Google.
- Invalid credentials show appropriate error messages.
- Authenticated users are redirected to Dashboard.
- Unauthenticated users accessing protected routes are redirected to Login.

---

### 5.3 Dashboard

**Priority:** P0 (Must Have)

| Requirement | Details |
|-------------|---------|
| Feature Cards | Clickable cards for: Know Your Kanoon, Upload & Chat, DocHub, Counter Argument Generator |
| Recent Activity | Last 5 interactions (chats, documents, uploads) |
| Saved Chats | Quick access to bookmarked/saved conversations |
| Saved Documents | Quick access to generated or uploaded documents |
| Welcome Banner | Personalized greeting with user's name and role |

**Acceptance Criteria:**
- Dashboard loads with user-specific data.
- Feature cards navigate to respective feature pages.
- Recent activity displays in reverse chronological order.
- Empty states shown when no activity/documents exist.

---

### 5.4 Know Your Kanoon

**Priority:** P0 (Must Have)

| Requirement | Details |
|-------------|---------|
| Chat Interface | Real-time conversational UI with message bubbles |
| Legal Q&A | User asks questions → AI responds with grounded answers |
| Indian Law Focus | Responses grounded in Indian statutes, case law, and constitutional provisions |
| Citations | Responses include source references (Act names, section numbers, case citations) |
| Context Awareness | Multi-turn conversation maintains context within a session |
| Disclaimers | Every response includes a disclaimer that it is not legal advice |
| New Chat | Users can start a new conversation at any time |
| Chat Persistence | Conversations are saved and accessible from Chat History |

**AI Behavior:**
- Use Gemini API with system prompts tuned for Indian legal domain.
- RAG pipeline (LangChain + ChromaDB) for grounding responses in legal texts.
- Confidence indicators where feasible.
- Clearly separate factual citations from AI interpretation.

**Acceptance Criteria:**
- User can ask a legal question and receive a response within 10 seconds.
- Responses cite relevant Indian laws or case names.
- Disclaimer is present on every AI response.
- Conversation history is preserved across page refreshes.

---

### 5.5 Upload & Chat

**Priority:** P0 (Must Have)

| Requirement | Details |
|-------------|---------|
| Supported Formats | PDF, DOCX, TXT |
| Max File Size | 10 MB per file |
| Upload Flow | Drag-and-drop or file picker → processing indicator → chat becomes available |
| Document Chat | User asks questions about the uploaded document |
| Summarization | "Summarize this document" capability |
| Clause Extraction | Identify and list key clauses, obligations, rights |
| Risk Analysis | Highlight potentially risky or unfavorable clauses |
| Legal Explanation | Explain legal jargon in plain language |

**AI Behavior:**
- Document text is extracted (PDF parsing, DOCX parsing).
- Extracted text is chunked and embedded into ChromaDB for the session.
- RAG queries are scoped to the uploaded document.
- Responses reference specific sections/pages of the document.

**Acceptance Criteria:**
- Files upload successfully with progress indication.
- Unsupported formats show clear error messages.
- Chat responses reference specific parts of the uploaded document.
- User can ask follow-up questions.

---

### 5.6 DocHub

**Priority:** P1 (Should Have)

| Requirement | Details |
|-------------|---------|
| Templates | Affidavit, Rental Agreement, NDA, Legal Notice, Power of Attorney |
| Template Selection | Grid/list view with descriptions and use-case guidance |
| AI-Assisted Generation | User fills key fields → AI generates complete document |
| Input Form | Dynamic form per template (party names, dates, terms, etc.) |
| Preview | Generated document shown in a formatted preview |
| Editing | User can edit the generated content before export |
| Export | Download as PDF or DOCX |
| Save | Save generated documents to user's account |

**Acceptance Criteria:**
- All 5 templates are available and functional.
- Generated documents are legally structured (not just freeform text).
- Users can edit content in a rich-text or markdown editor.
- Export produces well-formatted PDF/DOCX files.

---

### 5.7 Counter Argument Generator

**Priority:** P1 (Should Have)

| Requirement | Details |
|-------------|---------|
| Input | User provides a legal argument, claim, or position (text input) |
| Output | AI generates structured counter-arguments |
| Categories | Opposing arguments, Legal rebuttals, Procedural defenses, Alternative interpretations, Strategic perspectives |
| Citations | Counter-arguments cite relevant laws and precedents where possible |
| Multiple Perspectives | Generate arguments from multiple legal angles |
| Save | Users can save generated counter-arguments |

**Acceptance Criteria:**
- User inputs an argument and receives counter-arguments within 15 seconds.
- Output is structured into clear categories.
- Each counter-argument includes supporting reasoning.
- Disclaimer present indicating AI-generated nature.

---

### 5.8 User Profile

**Priority:** P1 (Should Have)

| Requirement | Details |
|-------------|---------|
| Display Info | Name, email, role, account creation date |
| Edit Profile | Update name and role |
| Preferences | Theme preference (light/dark), notification settings (future) |
| Account Actions | Change password (email/password users), logout |

**Acceptance Criteria:**
- Profile page displays correct user information.
- Users can update their name and role.
- Password change works for email/password accounts.

---

### 5.9 Chat History

**Priority:** P1 (Should Have)

| Requirement | Details |
|-------------|---------|
| Conversation List | All past conversations listed with title, date, feature source |
| Search | Search conversations by keyword |
| Resume | Click a conversation to resume it |
| Delete | Delete individual conversations |
| Generated Documents | Access previously generated documents |
| Uploaded Files | Access previously uploaded files and their chat sessions |

**Acceptance Criteria:**
- All conversations appear in reverse chronological order.
- Search returns relevant results.
- Resuming a conversation loads full context.
- Deletion is permanent with confirmation dialog.

---

## 6. Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Frontend** | React (JavaScript) | Widely adopted, component-based, large ecosystem |
| **Styling** | Tailwind CSS | Rapid UI development, utility-first, responsive by default |
| **Routing** | React Router v6 | Standard React routing solution |
| **HTTP Client** | Axios | Promise-based, interceptors for auth tokens |
| **Backend** | FastAPI (Python) | Async-ready, auto-generated docs, Python AI ecosystem compatibility |
| **Authentication** | Firebase Auth | Managed auth service, Google OAuth built-in, no custom auth code |
| **Database** | SQLite | Zero-config, file-based, sufficient for MVP traffic |
| **AI Model** | Gemini API | Google's latest LLM, strong reasoning, generous free tier |
| **RAG Framework** | LangChain | Standard RAG orchestration, document loaders, chunking |
| **Vector Store** | ChromaDB | Lightweight, embedded, Python-native vector database |
| **File Storage** | Local filesystem | Simple, no cloud dependency for MVP |

---

## 7. Technical Decisions Log

| # | Decision | Rationale | Alternatives Considered |
|---|----------|-----------|------------------------|
| 1 | Firebase Auth over custom JWT | Eliminates password hashing, token management, and OAuth implementation. Reduces security risk surface. | Custom JWT + bcrypt (more code, more risk) |
| 2 | SQLite over PostgreSQL | Zero-config, no separate server process, sufficient for MVP scale. Easy migration path to PostgreSQL later. | PostgreSQL (overkill for MVP), MongoDB (schema flexibility not needed) |
| 3 | ChromaDB over Pinecone | Runs locally, no API costs, Python-native, sufficient for MVP document volumes. | Pinecone (cloud dependency, cost), Weaviate (heavier setup) |
| 4 | Gemini API over OpenAI | Google ecosystem alignment, competitive quality, generous free/low-cost tier for MVP. | GPT-4 (higher cost), Claude (different ecosystem) |
| 5 | Monolithic architecture | Single FastAPI server handles all endpoints. Simplest deployment, easiest debugging. | Microservices (premature for MVP) |
| 6 | Local file storage over S3 | No cloud storage costs or configuration for MVP. Files stored on server filesystem. | AWS S3 (adds complexity and cost), Firebase Storage (adds dependency) |

---

## 8. User Flow Diagrams

### 8.1 Authentication Flow

```
Landing Page → [Login / Signup Button]
    ├── Email/Password Signup → Role Selection → Dashboard
    ├── Email/Password Login → Dashboard
    └── Google Login → Role Selection (first time) → Dashboard
```

### 8.2 Core Feature Flow

```
Dashboard
    ├── Know Your Kanoon → Chat Interface → Ask Question → AI Response (with citations + disclaimer)
    ├── Upload & Chat → Upload Document → Processing → Chat about Document
    ├── DocHub → Select Template → Fill Form → AI Generates → Preview → Edit → Export
    └── Counter Arguments → Input Argument → AI Generates Counter-Arguments → Save/Export
```

### 8.3 Data Persistence Flow

```
User Interaction
    ├── Chat Message → Saved to SQLite (conversations table)
    ├── Uploaded File → Saved to local storage + metadata in SQLite
    ├── Generated Document → Saved to local storage + metadata in SQLite
    └── All accessible via → Chat History / Dashboard
```

---

## 9. Legal & Ethical Constraints

These constraints are **non-negotiable** and must be enforced at both the system prompt level and the UI level.

| # | Constraint | Implementation |
|---|-----------|---------------|
| 1 | **Not Legal Advice** | Every AI response includes a footer disclaimer: *"This is AI-generated information, not legal advice. Consult a qualified lawyer for legal decisions."* |
| 2 | **Source Attribution** | AI responses must cite Act names, section numbers, or case names when referencing specific laws. |
| 3 | **Fact vs. Interpretation** | AI must clearly distinguish between what the law states (fact) and what it might mean in context (interpretation). |
| 4 | **Uncertainty Disclosure** | When the AI is uncertain or the query is ambiguous, it must explicitly state so. |
| 5 | **No Fabrication** | RAG grounding is used to minimize hallucination. Responses without supporting sources must caveat accordingly. |
| 6 | **Privacy** | Uploaded documents are stored locally, not shared across users, and not used for model training. |

---

## 10. UI/UX Principles

| Principle | Application |
|-----------|------------|
| **Simplicity** | Clean, uncluttered interfaces. No feature overload on any single screen. |
| **Accessibility** | Readable fonts (16px+ body), sufficient color contrast (WCAG AA), keyboard navigable. |
| **Responsiveness** | Mobile-first design. All features usable on mobile, optimized on desktop. |
| **Feedback** | Loading states, success/error toasts, progress indicators for uploads and AI processing. |
| **Consistency** | Unified color palette, typography, spacing, and component design across all pages. |
| **Dark Mode** | Support light and dark themes (user preference stored in profile). |

---

## 11. Scope Boundaries

### In Scope (MVP)

- Landing page with product information
- Firebase Authentication (email/password + Google)
- Dashboard with feature navigation and recent activity
- Know Your Kanoon (AI legal Q&A with RAG)
- Upload & Chat (document analysis)
- DocHub (5 templates with AI generation)
- Counter Argument Generator
- User Profile management
- Chat History with search and resume
- Local file storage
- SQLite database
- Basic error handling and loading states

### Out of Scope (MVP)

- Payment processing / subscription tiers
- Multi-language support
- Native mobile applications
- Real-time collaboration / shared workspaces
- Admin panel / user management dashboard
- Analytics and reporting
- API rate limiting / usage quotas
- Email notifications
- Lawyer directory / marketplace
- Court case tracking
- Advanced role-based access control (beyond role labeling)
- CI/CD pipeline setup
- Production deployment (Dockerization, cloud hosting)

---

## 12. Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|------------|
| **AI Hallucination** | Users receive incorrect legal information | High | RAG grounding, disclaimers, confidence indicators, source attribution |
| **Gemini API Rate Limits** | Service degradation during peak usage | Medium | Implement request queuing, graceful error handling, retry logic |
| **SQLite Concurrency** | Write locks under concurrent users | Low (MVP) | Acceptable for MVP scale; migration path to PostgreSQL documented |
| **Large File Uploads** | Server memory issues with large PDFs | Medium | Enforce 10MB limit, stream processing, chunked parsing |
| **Firebase Auth Dependency** | Outage blocks all authentication | Low | Firebase has 99.95% SLA; no cost-effective alternative for MVP |
| **Legal Accuracy** | Users rely on AI output for real legal decisions | High | Persistent disclaimers, never claim to replace legal counsel |

---

## 13. Success Criteria (MVP Launch)

| Criteria | Target |
|----------|--------|
| All 9 features functional and accessible | 100% |
| AI responses include citations in ≥80% of legal queries | ≥80% |
| Page load time (landing, dashboard) | < 3 seconds |
| AI response time (Q&A, document chat) | < 15 seconds |
| File upload + processing time (10MB PDF) | < 30 seconds |
| Zero critical bugs on core user flows | 0 critical bugs |
| Disclaimer present on every AI response | 100% |

---

## 14. Future Roadmap (Post-MVP)

| Phase | Features |
|-------|----------|
| **Phase 2** | Hindi language support, payment integration (Razorpay), PostgreSQL migration |
| **Phase 3** | Mobile app (React Native), advanced RAG with Indian Kanoon API, user analytics |
| **Phase 4** | Lawyer marketplace, real-time collaboration, court case tracking |
| **Phase 5** | API platform for third-party integrations, enterprise features |

---

## 15. Glossary

| Term | Definition |
|------|-----------|
| **RAG** | Retrieval-Augmented Generation — technique where AI retrieves relevant documents before generating a response |
| **ChromaDB** | An open-source, lightweight vector database for storing and querying embeddings |
| **LangChain** | A framework for developing applications powered by language models |
| **Know Your Kanoon** | NYAAY AI's legal Q&A feature (Kanoon = Law in Hindi) |
| **DocHub** | NYAAY AI's legal document generation feature |
| **Gemini API** | Google's large language model API |
| **Firebase Auth** | Google's managed authentication service |

---

> **Next Step:** Upon approval of this PRD, the next document to be generated is `ARCHITECTURE.md`.
