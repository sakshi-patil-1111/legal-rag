# NYAAY AI — Architecture Document

> **Version:** 2.0
> **Date:** 2026-06-23
> **Author:** Ansh Darji
> **Status:** Approved
> **References:** [PRD_v2.md](./PRD_v2.md)

---

## 1. High-Level System Architecture

### 1.1 Architecture Overview

NYAAY AI follows a **monolithic client-server architecture** with a clear separation between the React frontend (SPA) and the FastAPI backend. Firebase handles authentication externally, while Gemini API provides AI capabilities. ChromaDB runs embedded within the backend process.

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CLIENT (Browser)                          │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    React SPA (JavaScript)                     │  │
│  │                                                               │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────┐  │  │
│  │  │  Pages   │ │Components│ │ Services │ │  Auth Context  │  │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────────────┘  │  │
│  │                                                               │  │
│  │  Tailwind CSS  │  React Router  │  Axios (HTTP Client)       │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│                   Firebase Auth SDK                                 │
└──────────────────────────────┼──────────────────────────────────────┘
                               │
                    ┌──────────┼──────────┐
                    │  HTTPS / REST API   │
                    └──────────┼──────────┘
                               │
┌──────────────────────────────┼──────────────────────────────────────┐
│                        SERVER (FastAPI)                              │
│                                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────┐ │
│  │  API Layer  │  │Service Layer│  │       AI / RAG Layer        │ │
│  │  (Routes)   │──│  (Business  │──│                             │ │
│  │             │  │   Logic)    │  │  LangChain  │  Gemini API   │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────────┘ │
│         │                │                        │                 │
│  ┌──────┴──────┐  ┌──────┴──────┐  ┌──────────────┴──────────────┐ │
│  │  Firebase   │  │   SQLite    │  │         ChromaDB            │ │
│  │  Admin SDK  │  │  Database   │  │      (Vector Store)         │ │
│  │  (Verify)   │  │             │  │                             │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────────┘ │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │              Local Filesystem (Uploads + Exports)              │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────┐
                    │   EXTERNAL SERVICES │
                    │                     │
                    │  ┌───────────────┐  │
                    │  │ Firebase Auth │  │
                    │  │   (Google)    │  │
                    │  └───────────────┘  │
                    │                     │
                    │  ┌───────────────┐  │
                    │  │  Gemini API   │  │
                    │  │   (Google)    │  │
                    │  └───────────────┘  │
                    └─────────────────────┘
```

### 1.2 Component Responsibilities

| Component | Responsibility | Runs On |
|-----------|---------------|---------|
| **React SPA** | UI rendering, routing, user interactions, form handling | Browser |
| **Firebase Auth SDK** | User signup/login, token generation, Google OAuth | Browser + Google Cloud |
| **FastAPI Server** | REST API, business logic, AI orchestration, file handling, rate limiting | Local server |
| **Firebase Admin SDK** | Verify ID tokens on backend, extract user identity | Local server |
| **SQLite** | Persistent storage for users, conversations, documents | Local file |
| **ChromaDB** | Vector storage for document embeddings (RAG) | Embedded in backend process |
| **LangChain** | RAG orchestration — document loading, chunking, retrieval chain | Backend process |
| **Gemini API** | LLM inference — legal Q&A, document analysis, generation | Google Cloud (external) |
| **Local Filesystem** | Store uploaded files and exported documents | Local disk |

### 1.3 Communication Patterns

```
Browser ──[HTTPS/REST + JSON]──▶ FastAPI
Browser ──[Firebase SDK]───────▶ Firebase Auth (Google Cloud)
FastAPI ──[Firebase Admin SDK]─▶ Firebase Auth (Token Verification)
FastAPI ──[Gemini Python SDK]──▶ Gemini API (Google Cloud)
FastAPI ──[Python API]─────────▶ SQLite (Local File)
FastAPI ──[Python API]─────────▶ ChromaDB (Embedded)
FastAPI ──[OS File I/O]────────▶ Local Filesystem
```

**Key Design Decision:** All external service calls (Firebase verify, Gemini API) happen exclusively on the backend. The frontend only communicates with Firebase Auth SDK for login/signup and with the FastAPI backend for everything else. This keeps API keys secure on the server side.

---

## 2. User Request Flows

### 2.1 Authentication Flow

```
┌──────────┐     ┌──────────────┐     ┌──────────┐     ┌──────────┐
│  Browser │     │ Firebase Auth│     │  FastAPI  │     │  SQLite  │
└────┬─────┘     └──────┬───────┘     └────┬─────┘     └────┬─────┘
     │                  │                  │                 │
     │  1. Signup/Login │                  │                 │
     │─────────────────▶│                  │                 │
     │                  │                  │                 │
     │  2. ID Token     │                  │                 │
     │◀─────────────────│                  │                 │
     │                  │                  │                 │
     │  3. POST /api/auth/register         │                 │
     │     {id_token, role}                │                 │
     │────────────────────────────────────▶│                 │
     │                  │                  │                 │
     │                  │  4. Verify Token │                 │
     │                  │◀─────────────────│                 │
     │                  │                  │                 │
     │                  │  5. Token Valid  │                 │
     │                  │─────────────────▶│                 │
     │                  │                  │                 │
     │                  │                  │  6. Upsert User │
     │                  │                  │────────────────▶│
     │                  │                  │                 │
     │  7. User Profile + Session         │                 │
     │◀────────────────────────────────────│                 │
     │                  │                  │                 │
```

**Flow Details:**

1. **User initiates signup/login** via Firebase Auth SDK on the frontend (email/password or Google).
2. **Firebase returns an ID token** (JWT signed by Google) to the frontend.
3. **Frontend sends ID token to backend** with role selection (signup) or without (login).
4. **Backend verifies token** using Firebase Admin SDK — this validates the token signature, expiry, and issuer.
5. **Firebase confirms validity** and returns decoded token with `uid`, `email`, `name`.
6. **Backend upserts user** in SQLite — creates new user on first login, updates `last_login` on subsequent logins.
7. **Backend returns user profile** to frontend.

**Subsequent Requests:** Frontend includes the Firebase ID token in the `Authorization: Bearer <token>` header on every API request. Backend verifies it via middleware.

---

### 2.2 Know Your Kanoon Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Browser │     │  FastAPI  │     │ LangChain│     │ ChromaDB │     │  Gemini  │
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │                 │                 │
     │ 1. User sends  │                │                 │                 │
     │    question     │                │                 │                 │
     │───────────────▶│                │                 │                 │
     │                │                │                 │                 │
     │                │ 2. Build RAG   │                 │                 │
     │                │    query       │                 │                 │
     │                │───────────────▶│                 │                 │
     │                │                │                 │                 │
     │                │                │ 3. Retrieve     │                 │
     │                │                │    relevant     │                 │
     │                │                │    legal texts  │                 │
     │                │                │────────────────▶│                 │
     │                │                │                 │                 │
     │                │                │ 4. Ranked       │                 │
     │                │                │    chunks       │                 │
     │                │                │◀────────────────│                 │
     │                │                │                 │                 │
     │                │                │ 5. Build prompt │                 │
     │                │                │    (question +  │                 │
     │                │                │    context +    │                 │
     │                │                │    system)      │                 │
     │                │                │────────────────────────────────▶│
     │                │                │                 │                 │
     │                │                │ 6. AI Response  │                 │
     │                │                │◀────────────────────────────────│
     │                │                │                 │                 │
     │                │ 7. Format +    │                 │                 │
     │                │    add disclaimer               │                 │
     │                │◀───────────────│                 │                 │
     │                │                │                 │                 │
     │ 8. Response    │                │                 │                 │
     │    with citations               │                 │                 │
     │◀───────────────│                │                 │                 │
     │                │                │                 │                 │
     │                │ 9. Save to     │                 │                 │
     │                │    SQLite      │                 │                 │
     │                │ (async)        │                 │                 │
```

**Key Design Decisions:**

- RAG retrieval happens **before** the Gemini call to provide grounding context.
- The system prompt instructs Gemini to cite sources from the retrieved context and separate facts from interpretation.
- Conversation history (last N messages) is included in the prompt for multi-turn context.
- The disclaimer is appended server-side, not client-side, to ensure it cannot be bypassed.

---

### 2.3 Upload & Chat Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Browser │     │  FastAPI  │     │ LangChain│     │ ChromaDB │     │  Gemini  │
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │                 │                 │
     │ 1. Upload file │                │                 │                 │
     │   (PDF/DOCX/   │                │                 │                 │
     │    TXT)         │                │                 │                 │
     │───────────────▶│                │                 │                 │
     │                │                │                 │                 │
     │                │ 2. Save file   │                 │                 │
     │                │    to disk     │                 │                 │
     │                │                │                 │                 │
     │                │ 3. Extract     │                 │                 │
     │                │    text        │                 │                 │
     │                │───────────────▶│                 │                 │
     │                │                │                 │                 │
     │                │                │ 4. Chunk text   │                 │
     │                │                │    + embed      │                 │
     │                │                │────────────────▶│                 │
     │                │                │                 │                 │
     │ 5. Upload      │                │                 │                 │
     │    complete     │                │                 │                 │
     │◀───────────────│                │                 │                 │
     │                │                │                 │                 │
     │ 6. User asks   │                │                 │                 │
     │    question     │                │                 │                 │
     │───────────────▶│                │                 │                 │
     │                │                │                 │                 │
     │                │ 7. RAG query   │                 │                 │
     │                │    (scoped to  │                 │                 │
     │                │    document    │                 │                 │
     │                │    collection) │                 │                 │
     │                │───────────────▶│────────────────▶│                 │
     │                │                │◀────────────────│                 │
     │                │                │                 │                 │
     │                │                │ 8. Prompt +     │                 │
     │                │                │    doc context  │                 │
     │                │                │────────────────────────────────▶│
     │                │                │◀────────────────────────────────│
     │                │                │                 │                 │
     │ 9. Response    │                │                 │                 │
     │◀───────────────│                │                 │                 │
```

**Key Design Decisions:**

- Each uploaded document gets its own **ChromaDB collection** (named by document ID), so RAG queries are automatically scoped to that document.
- Text extraction uses LangChain's document loaders: `PyPDFLoader` for PDF, `Docx2txtLoader` for DOCX, `TextLoader` for TXT.
- Upload is a **synchronous** operation for MVP — the user waits for processing to complete before chatting. For large files (up to 10MB), this should complete within 30 seconds.
- Maximum page count enforced: **300 pages** for PDFs. Page count is checked after file save but before text extraction. Files exceeding 300 pages are rejected and deleted.

---

### 2.4 DocHub Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Browser │     │  FastAPI  │     │  Gemini  │     │  SQLite  │
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │                 │
     │ 1. Select      │                │                 │
     │    template     │                │                 │
     │───────────────▶│                │                 │
     │                │                │                 │
     │ 2. Template    │                │                 │
     │    form schema │                │                 │
     │◀───────────────│                │                 │
     │                │                │                 │
     │ 3. Submit      │                │                 │
     │    form data   │                │                 │
     │───────────────▶│                │                 │
     │                │                │                 │
     │                │ 4. Build prompt│                 │
     │                │    (template + │                 │
     │                │    user data)  │                 │
     │                │───────────────▶│                 │
     │                │                │                 │
     │                │ 5. Generated   │                 │
     │                │    document    │                 │
     │                │◀───────────────│                 │
     │                │                │                 │
     │ 6. Preview     │                │                 │
     │◀───────────────│                │                 │
     │                │                │                 │
     │ 7. Edit +      │                │                 │
     │    Export       │                │                 │
     │───────────────▶│                │                 │
     │                │                │                 │
     │                │ 8. Save        │                 │
     │                │    metadata    │                 │
     │                │───────────────────────────────▶│
     │                │                │                 │
     │ 9. Download    │                │                 │
     │    (PDF/DOCX)  │                │                 │
     │◀───────────────│                │                 │
```

**Key Design Decisions:**

- Templates are **stored as prompt templates** on the backend (not in the database). Each template defines: required fields, prompt structure, and output format.
- MVP includes **3 templates**: Legal Notice, Rental Agreement, Affidavit. NDA and Power of Attorney are deferred to Phase 2.
- DocHub does **not** use RAG — it uses direct Gemini prompting with structured templates. RAG would add latency without significant benefit since document generation is template-driven.
- Export to PDF/DOCX is handled server-side using Python libraries (`reportlab` for PDF, `python-docx` for DOCX).

---

### 2.5 Counter Argument Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Browser │     │  FastAPI  │     │ LangChain│     │ ChromaDB │     │  Gemini  │
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │                 │                 │
     │ 1. Submit      │                │                 │                 │
     │    legal       │                │                 │                 │
     │    argument    │                │                 │                 │
     │───────────────▶│                │                 │                 │
     │                │                │                 │                 │
     │                │ 2. RAG query   │                 │                 │
     │                │    for related │                 │                 │
     │                │    legal texts │                 │                 │
     │                │───────────────▶│────────────────▶│                 │
     │                │                │◀────────────────│                 │
     │                │                │                 │                 │
     │                │                │ 3. Build prompt │                 │
     │                │                │    (argument +  │                 │
     │                │                │    context +    │                 │
     │                │                │    counter      │                 │
     │                │                │    template)    │                 │
     │                │                │────────────────────────────────▶│
     │                │                │                 │                 │
     │                │                │ 4. Structured   │                 │
     │                │                │    counter-     │                 │
     │                │                │    arguments    │                 │
     │                │                │◀────────────────────────────────│
     │                │                │                 │                 │
     │ 5. Categorized │                │                 │                 │
     │    counter-    │                │                 │                 │
     │    arguments   │                │                 │                 │
     │◀───────────────│                │                 │                 │
```

**Key Design Decisions:**

- Counter Argument Generator **uses RAG** (unlike DocHub) because counter-arguments benefit from being grounded in actual legal precedents and statutes.
- The system prompt instructs Gemini to structure output into **4 categories**: Opposing Viewpoints, Legal Rebuttals, Alternative Interpretations, Strategic Perspectives.
- Output is returned as structured JSON, which the frontend renders into categorized sections.

---

## 3. Frontend Architecture

### 3.1 Architecture Pattern

The frontend uses a **page-based architecture** with shared components and a service layer for API communication.

```
┌─────────────────────────────────────────────────────┐
│                    React App                        │
│                                                     │
│  ┌───────────────────────────────────────────────┐  │
│  │               Router (React Router v6)        │  │
│  │                                               │  │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────────┐  │  │
│  │  │ Public  │  │Protected│  │   Layout     │  │  │
│  │  │ Routes  │  │ Routes  │  │  Wrappers    │  │  │
│  │  └─────────┘  └─────────┘  └─────────────┘  │  │
│  └───────────────────────────────────────────────┘  │
│                                                     │
│  ┌────────────┐  ┌────────────┐  ┌──────────────┐  │
│  │   Pages    │  │ Components │  │   Layouts    │  │
│  │            │  │            │  │              │  │
│  │ LandingPage│  │ ChatBubble │  │ AuthLayout   │  │
│  │ Login      │  │ FileUpload │  │ DashLayout   │  │
│  │ Signup     │  │ FeatureCard│  │              │  │
│  │ Dashboard  │  │ DocPreview │  │              │  │
│  │ KnowKanoon │  │ Sidebar    │  │              │  │
│  │ UploadChat │  │ Navbar     │  │              │  │
│  │ DocHub     │  │ Disclaimer │  │              │  │
│  │ CounterArg │  │ ...        │  │              │  │
│  │ Profile    │  │            │  │              │  │
│  │ History    │  │            │  │              │  │
│  └────────────┘  └────────────┘  └──────────────┘  │
│                                                     │
│  ┌────────────┐  ┌────────────┐  ┌──────────────┐  │
│  │  Services  │  │  Context   │  │    Utils     │  │
│  │            │  │            │  │              │  │
│  │ api.js     │  │ AuthContext│  │ formatDate   │  │
│  │ authSvc    │  │ ThemeCtx   │  │ validators   │  │
│  │ chatSvc    │  │            │  │ constants    │  │
│  │ docSvc     │  │            │  │              │  │
│  │ uploadSvc  │  │            │  │              │  │
│  └────────────┘  └────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────┘
```

### 3.2 Pages

| Page | Route | Auth Required | Description |
|------|-------|:---:|-------------|
| `LandingPage` | `/` | No | Hero, features, CTAs |
| `LoginPage` | `/login` | No | Email/password + Google login |
| `SignupPage` | `/signup` | No | Registration with role selection |
| `DashboardPage` | `/dashboard` | Yes | Feature cards, recent activity |
| `KnowKanoonPage` | `/know-your-kanoon` | Yes | Legal Q&A chat interface |
| `UploadChatPage` | `/upload-chat` | Yes | File upload + document chat |
| `DocHubPage` | `/dochub` | Yes | Template selection grid |
| `DocHubGeneratePage` | `/dochub/:templateId` | Yes | Template form + generation |
| `CounterArgumentPage` | `/counter-arguments` | Yes | Argument input + results |
| `ProfilePage` | `/profile` | Yes | User info + preferences |
| `ChatHistoryPage` | `/history` | Yes | All past conversations |
| `ChatDetailPage` | `/history/:chatId` | Yes | Resume a past conversation |

### 3.3 Component Hierarchy

```
App
├── AuthProvider (Context)
│   ├── ThemeProvider (Context)
│   │   ├── Router
│   │   │   ├── PublicLayout
│   │   │   │   ├── Navbar (public variant)
│   │   │   │   ├── LandingPage
│   │   │   │   ├── LoginPage
│   │   │   │   └── SignupPage
│   │   │   │
│   │   │   ├── ProtectedRoute (wrapper)
│   │   │   │   ├── DashboardLayout
│   │   │   │   │   ├── Sidebar
│   │   │   │   │   ├── TopBar (user info, logout)
│   │   │   │   │   └── Page Content
│   │   │   │   │       ├── DashboardPage
│   │   │   │   │       ├── KnowKanoonPage
│   │   │   │   │       │   ├── ChatSidebar (conversation list)
│   │   │   │   │       │   ├── ChatWindow
│   │   │   │   │       │   │   ├── ChatBubble (user)
│   │   │   │   │       │   │   ├── ChatBubble (AI + Disclaimer)
│   │   │   │   │       │   │   └── ChatInput
│   │   │   │   │       │   └── CitationPanel
│   │   │   │   │       ├── UploadChatPage
│   │   │   │   │       │   ├── FileUploader (drag & drop)
│   │   │   │   │       │   ├── ProcessingIndicator
│   │   │   │   │       │   └── ChatWindow (reused)
│   │   │   │   │       ├── DocHubPage
│   │   │   │   │       │   └── TemplateCard (×3)
│   │   │   │   │       ├── DocHubGeneratePage
│   │   │   │   │       │   ├── DynamicForm
│   │   │   │   │       │   ├── DocumentPreview
│   │   │   │   │       │   └── ExportButtons
│   │   │   │   │       ├── CounterArgumentPage
│   │   │   │   │       │   ├── ArgumentInput
│   │   │   │   │       │   └── CounterArgumentResults
│   │   │   │   │       │       └── ArgumentCategory (×4)
│   │   │   │   │       ├── ProfilePage
│   │   │   │   │       └── ChatHistoryPage
│   │   │   │   │           └── ConversationListItem
```

### 3.4 Shared / Reusable Components

| Component | Used By | Purpose |
|-----------|---------|---------|
| `ChatBubble` | KnowKanoon, UploadChat | Renders a single chat message (user or AI) |
| `ChatInput` | KnowKanoon, UploadChat | Text input with send button |
| `ChatWindow` | KnowKanoon, UploadChat | Scrollable chat message container |
| `Disclaimer` | KnowKanoon, UploadChat, CounterArg | AI disclaimer footer text |
| `FileUploader` | UploadChat | Drag-and-drop + file picker |
| `FeatureCard` | Dashboard, Landing | Clickable card with icon, title, description |
| `Sidebar` | All dashboard pages | Navigation sidebar |
| `TopBar` | All dashboard pages | User avatar, name, logout |
| `LoadingSpinner` | All pages | Loading state indicator |
| `EmptyState` | Dashboard, History | "No data yet" placeholder |
| `Toast` | Global | Success/error notifications |
| `Modal` | History (delete confirm), Profile | Confirmation dialogs |

### 3.5 Services Layer

The services layer abstracts all API communication. Each service file maps to a backend resource.

| Service File | Responsibility |
|-------------|---------------|
| `api.js` | Axios instance with base URL, auth token interceptor, error handler, rate limit (429) handler |
| `authService.js` | `register()`, `login()`, `googleLogin()`, `logout()`, `getCurrentUser()` |
| `chatService.js` | `sendMessage()`, `getConversations()`, `getConversation()`, `deleteConversation()` |
| `uploadService.js` | `uploadFile()`, `chatWithDocument()`, `getUploads()` |
| `docService.js` | `getTemplates()`, `generateDocument()`, `exportDocument()`, `getSavedDocs()` |
| `counterArgService.js` | `generateCounterArgs()`, `saveCounterArgs()` |
| `profileService.js` | `getProfile()`, `updateProfile()`, `changePassword()` |
| `historyService.js` | `getHistory()`, `searchHistory()`, `deleteHistory()` |

**Axios Interceptor Pattern:**

```
Every outgoing request:
  1. Get Firebase ID token from AuthContext
  2. Attach as Authorization: Bearer <token>
  3. Send request

Every response error:
  401 → Redirect to /login, clear local auth state
  429 → Show "Rate limit exceeded" toast, suggest waiting
```

### 3.6 Routing Strategy

**Two layout zones:**

1. **Public Layout** — Landing, Login, Signup (no sidebar, public navbar)
2. **Dashboard Layout** — All authenticated pages (sidebar + top bar)

**Route protection:**
- `ProtectedRoute` component wraps all dashboard routes.
- Checks `AuthContext` for authenticated user.
- Redirects to `/login` if not authenticated.
- Redirects to `/dashboard` if authenticated user hits `/login` or `/signup`.

### 3.7 State Management Strategy

**No Redux. No Zustand. React Context + local state only.**

| State Type | Strategy | Rationale |
|-----------|----------|-----------|
| **Auth state** | `AuthContext` (React Context) | Global — needed by all protected routes and API interceptor |
| **Theme** | `ThemeContext` (React Context) | Global — light/dark mode across all pages |
| **Page data** | `useState` + `useEffect` in each page | Local — conversations, documents, form data |
| **Chat messages** | `useState` in chat pages | Local — managed per page session |
| **Form inputs** | `useState` in form components | Local — standard React pattern |

**Why no state library:** For an MVP with 10 pages, React Context + local state is sufficient. Adding Redux/Zustand would violate the "avoid overengineering" principle. If the app grows beyond 20+ pages with complex shared state, Zustand can be introduced later.

---

## 4. Backend Architecture

### 4.1 Architecture Pattern

The backend follows a **3-layer architecture**: API Layer → Service Layer → Data Layer. An additional AI/RAG layer handles all LLM and vector store interactions.

```
┌─────────────────────────────────────────────────────────────┐
│                        API LAYER                            │
│                   (FastAPI Route Handlers)                   │
│                                                             │
│  auth_routes  │  chat_routes  │  upload_routes  │  doc_routes│
│  counter_routes  │  profile_routes  │  history_routes       │
└────────────────────────────┬────────────────────────────────┘
                             │
                    Dependency Injection
                             │
┌────────────────────────────┼────────────────────────────────┐
│                      SERVICE LAYER                          │
│                  (Business Logic + Orchestration)            │
│                                                             │
│  auth_service  │  chat_service  │  upload_service           │
│  doc_service   │  counter_service  │  profile_service       │
│  history_service                                            │
└──────────┬──────────────┬──────────────┬────────────────────┘
           │              │              │
     ┌─────┘        ┌─────┘        ┌─────┘
     │              │              │
┌────┴────┐   ┌─────┴─────┐  ┌────┴──────────────────────────┐
│  DATA   │   │   FILE    │  │         AI / RAG LAYER        │
│  LAYER  │   │ PROCESSING│  │                                │
│         │   │   LAYER   │  │  ┌──────────┐  ┌───────────┐  │
│ SQLite  │   │           │  │  │ LangChain│  │ Gemini    │  │
│ (CRUD)  │   │ PDF Parse │  │  │ (RAG)    │  │ (LLM)     │  │
│         │   │ DOCX Parse│  │  │          │  │           │  │
│         │   │ TXT Read  │  │  │ ChromaDB │  │ Prompts   │  │
│         │   │           │  │  │ (Vectors)│  │ (Templates│  │
│         │   │ PDF Export│  │  │          │  │           │  │
│         │   │ DOCX Export│ │  └──────────┘  └───────────┘  │
└─────────┘   └───────────┘  └────────────────────────────────┘
```

### 4.2 API Layer

The API layer handles HTTP concerns only: request parsing, validation, response formatting, auth middleware, and rate limiting.

| Router File | Prefix | Responsibilities |
|-------------|--------|-----------------|
| `auth_routes.py` | `/api/auth` | Register, login verification, token refresh |
| `chat_routes.py` | `/api/chat` | Send message, get conversations, get/delete conversation |
| `upload_routes.py` | `/api/upload` | Upload file, chat with document, list uploads |
| `doc_routes.py` | `/api/documents` | Get templates, generate document, export, list saved |
| `counter_routes.py` | `/api/counter` | Generate counter-arguments, save results |
| `profile_routes.py` | `/api/profile` | Get/update profile, change password |
| `history_routes.py` | `/api/history` | List all history, search, delete |

### 4.3 Service Layer

Each service encapsulates business logic and orchestrates calls to the data layer and AI layer.

| Service | Key Methods | Dependencies |
|---------|------------|-------------|
| `auth_service.py` | `verify_token()`, `register_user()`, `get_or_create_user()` | Firebase Admin, SQLite |
| `chat_service.py` | `process_message()`, `get_conversation()`, `list_conversations()` | AI Service, SQLite |
| `upload_service.py` | `process_upload()`, `chat_with_document()` | File Processor, RAG Service, SQLite |
| `doc_service.py` | `get_templates()`, `generate_document()`, `export_document()` | AI Service, File Exporter, SQLite |
| `counter_service.py` | `generate_counter_arguments()` | RAG Service, AI Service, SQLite |
| `profile_service.py` | `get_profile()`, `update_profile()` | SQLite |
| `history_service.py` | `get_all_history()`, `search()`, `delete()` | SQLite |

### 4.4 AI Layer

Centralized module for all Gemini API interactions.

| Component | Purpose |
|-----------|---------|
| `gemini_client.py` | Wrapper around Gemini Python SDK. Handles API key, model selection, 30s timeout, 3 retries with exponential backoff (1s, 2s, 4s), error categorization (rate limit vs. server error vs. timeout), and user-friendly error messages. See Gemini Failure Handling section. |
| `prompts/` directory | Stores all system prompts as separate text/template files. |
| `prompts/know_kanoon_system.txt` | System prompt for legal Q&A — instructs Gemini on Indian law focus, citation format, disclaimer requirements. |
| `prompts/upload_chat_system.txt` | System prompt for document analysis — scoped to uploaded document context. |
| `prompts/doc_gen_system.txt` | System prompt for document generation — template-aware, legally structured output. |
| `prompts/counter_arg_system.txt` | System prompt for counter-arguments — structured output with 4 categories. |

**Why separate prompt files:** Prompts are treated as configuration, not code. Changing a prompt should not require code changes. This also makes prompts version-controllable and reviewable.

### 4.5 Gemini Failure Handling Strategy

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
- If Gemini is down, affected features show an error state (not a crash).
- Non-AI features (dashboard, profile, history listing) continue to work.
- Error messages are user-friendly, never expose technical details.
- All Gemini failures are logged with request ID, error type, retry count.

#### Logging
- Log every Gemini API call: timestamp, feature, input token count, output token count, latency, success/failure.
- Do NOT log: full prompt text (contains user data), full response text.
- Log error details: error code, error message, retry attempt number.

### 4.6 RAG Layer

| Component | Purpose |
|-----------|---------|
| `rag_service.py` | Orchestrates the full RAG pipeline: embed query → retrieve → build context → call LLM. |
| `document_processor.py` | Extracts text from PDF/DOCX/TXT using LangChain document loaders. |
| `chunking.py` | Splits extracted text into chunks using `RecursiveCharacterTextSplitter`. |
| `embedding_service.py` | Generates embeddings using Gemini's embedding model (`models/embedding-001`). |
| `vector_store.py` | Manages ChromaDB collections — create, add, query, delete. |
| `retriever.py` | Queries ChromaDB and returns ranked, relevant chunks with metadata. |

### 4.7 File Processing Layer

| Component | Purpose |
|-----------|---------|
| `file_parser.py` | Unified interface for text extraction. Dispatches to the correct parser based on file extension. |
| `pdf_parser.py` | Extracts text from PDF using `PyPDF2` (via LangChain's `PyPDFLoader`). |
| `docx_parser.py` | Extracts text from DOCX using `docx2txt` (via LangChain's `Docx2txtLoader`). |
| `txt_parser.py` | Reads plain text files. |
| `pdf_exporter.py` | Generates PDF documents from content using `reportlab`. |
| `docx_exporter.py` | Generates DOCX documents from content using `python-docx`. |

#### Upload Validation Pipeline

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

### 4.8 Middleware & Dependencies

| Middleware | Purpose |
|-----------|---------|
| `auth_middleware.py` | FastAPI dependency that extracts Bearer token, verifies via Firebase Admin SDK, and injects `current_user` into route handlers. |
| `cors_middleware` | Configured via FastAPI's `CORSMiddleware`. Allows requests from `localhost:5173` (Vite dev server). |
| `error_handler.py` | Global exception handler that formats all errors into consistent JSON responses. No stack traces in production. |
| `rate_limiter` | `slowapi` rate limiting middleware. See Rate Limiting Design section. |

---

## 5. Database Architecture

### 5.1 Core Entities

NYAAY AI uses **6 tables** in SQLite. The schema is intentionally minimal — only store what's needed for MVP.

```
┌──────────────┐       ┌──────────────────┐       ┌──────────────┐
│    users     │       │  conversations   │       │   messages   │
├──────────────┤       ├──────────────────┤       ├──────────────┤
│ id (PK)      │──┐    │ id (PK)          │──┐    │ id (PK)      │
│ firebase_uid │  │    │ user_id (FK)     │  │    │ conv_id (FK) │
│ email        │  │    │ title            │  │    │ role         │
│ name         │  │    │ feature_type     │  │    │ content      │
│ role         │  ├───▶│ created_at       │  ├───▶│ citations    │
│ preferences  │  │    │ updated_at       │  │    │ created_at   │
│ created_at   │  │    │ is_active        │  │    └──────────────┘
│ last_login   │  │    └──────────────────┘  │
└──────────────┘  │                          │
                  │    ┌──────────────────┐  │
                  │    │    documents     │  │
                  │    ├──────────────────┤  │
                  │    │ id (PK)          │  │
                  ├───▶│ user_id (FK)     │  │
                  │    │ conv_id (FK)     │──┘
                  │    │ title            │
                  │    │ template_type    │
                  │    │ content          │
                  │    │ file_path        │
                  │    │ doc_type         │
                  │    │ created_at       │
                  │    └──────────────────┘
                  │
                  │    ┌──────────────────┐
                  │    │    uploads       │
                  │    ├──────────────────┤
                  │    │ id (PK)          │
                  ├───▶│ user_id (FK)     │
                  │    │ conv_id (FK)     │
                  │    │ original_name    │
                  │    │ file_path        │
                  │    │ file_type        │
                  │    │ file_size        │
                  │    │ page_count       │
                  │    │ chroma_collection│
                  │    │ status           │
                  │    │ created_at       │
                  │    └──────────────────┘
                  │
                  │    ┌──────────────────┐
                  │    │ counter_arguments│
                  │    ├──────────────────┤
                  │    │ id (PK)          │
                  └───▶│ user_id (FK)     │
                       │ input_argument   │
                       │ result_json      │
                       │ created_at       │
                       └──────────────────┘
```

### 5.2 Entity Details

#### `users`

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| `id` | INTEGER | PK, AUTOINCREMENT | Internal user ID |
| `firebase_uid` | TEXT | UNIQUE, NOT NULL | Firebase's unique user identifier |
| `email` | TEXT | UNIQUE, NOT NULL | User's email address |
| `name` | TEXT | NOT NULL | Display name |
| `role` | TEXT | NOT NULL, CHECK(role IN ('citizen', 'student', 'lawyer')) | One of: citizen, student, lawyer |
| `preferences` | TEXT | DEFAULT '{}' | JSON string for user preferences (theme, etc.) |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Account creation time |
| `last_login` | DATETIME | | Last login timestamp |

#### `conversations`

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| `id` | TEXT | PK | UUID string |
| `user_id` | INTEGER | FK → users.id, NOT NULL | Owning user |
| `title` | TEXT | NOT NULL | Auto-generated or user-set title |
| `feature_type` | TEXT | NOT NULL | One of: know_kanoon, upload_chat, counter_arg |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | |
| `updated_at` | DATETIME | | Updated on each new message |
| `is_active` | BOOLEAN | DEFAULT true | Soft delete flag |

#### `messages`

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| `id` | INTEGER | PK, AUTOINCREMENT | |
| `conversation_id` | TEXT | FK → conversations.id, NOT NULL | Parent conversation |
| `role` | TEXT | NOT NULL | 'user' or 'assistant' |
| `content` | TEXT | NOT NULL | Message text content |
| `citations` | TEXT | DEFAULT NULL | JSON string of cited sources |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | |

#### `documents`

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| `id` | TEXT | PK | UUID string |
| `user_id` | INTEGER | FK → users.id, NOT NULL | Owning user |
| `conversation_id` | TEXT | FK → conversations.id, NULLABLE | Linked conversation (if generated during chat) |
| `title` | TEXT | NOT NULL | Document title |
| `template_type` | TEXT | NULLABLE, CHECK(template_type IN ('legal_notice', 'rental_agreement', 'affidavit')) | Template used for generation |
| `content` | TEXT | NOT NULL | Document content (markdown/text) |
| `file_path` | TEXT | NULLABLE | Path to exported file on disk |
| `doc_type` | TEXT | NOT NULL | 'generated' or 'exported' |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | |

#### `uploads`

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| `id` | TEXT | PK | UUID string |
| `user_id` | INTEGER | FK → users.id, NOT NULL | Owning user |
| `conversation_id` | TEXT | FK → conversations.id, NULLABLE | Linked conversation |
| `original_name` | TEXT | NOT NULL | Original uploaded filename |
| `file_path` | TEXT | NOT NULL | Path to stored file on disk |
| `file_type` | TEXT | NOT NULL | 'pdf', 'docx', or 'txt' |
| `file_size` | INTEGER | NOT NULL | File size in bytes |
| `page_count` | INTEGER | NULLABLE | Page count (PDF only) |
| `chroma_collection` | TEXT | NOT NULL | ChromaDB collection name for this document's vectors |
| `status` | TEXT | NOT NULL, DEFAULT 'processing' | One of: processing, ready, error |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | |

#### `counter_arguments`

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| `id` | TEXT | PK | UUID string |
| `user_id` | INTEGER | FK → users.id, NOT NULL | Owning user |
| `input_argument` | TEXT | NOT NULL | The original argument provided by user |
| `result_json` | TEXT | NOT NULL | Full structured JSON output from AI |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | |

### 5.3 Relationships

```
users (1) ──── (N) conversations
users (1) ──── (N) documents
users (1) ──── (N) uploads
users (1) ──── (N) counter_arguments
conversations (1) ──── (N) messages
conversations (1) ──── (0..1) uploads        (Upload & Chat has one file per conversation)
conversations (1) ──── (0..N) documents      (DocHub may link generated docs to a conversation)
```

### 5.4 Data Ownership

**Every row in every table is owned by a user.** All queries are filtered by `user_id` to ensure data isolation. A user can never access another user's conversations, documents, uploads, or counter-arguments.

### 5.5 Why These Tables Only

| Decision | Rationale |
|----------|-----------|
| No separate `sessions` table | Firebase handles session management. We only store `last_login`. |
| No `tags` or `categories` table | MVP doesn't require content categorization beyond `feature_type`. |
| `preferences` as JSON column | Avoids a separate key-value table for a handful of settings. |
| `citations` as JSON column | Citations are unstructured and variable — a separate table would be over-normalized. |
| `counter_arguments` as a standalone table | Counter-args are single-shot outputs (not multi-turn conversations), so they don't fit the conversations + messages model. |

---

## 6. Firebase Authentication Architecture

### 6.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                           FRONTEND                                  │
│                                                                     │
│  ┌──────────────────┐    ┌────────────────────────────────────────┐ │
│  │ Firebase Auth SDK │    │           AuthContext                  │ │
│  │                   │    │                                        │ │
│  │ • signUp()        │    │ • user (current Firebase user)         │ │
│  │ • signIn()        │    │ • loading (auth state loading)         │ │
│  │ • googleSignIn()  │    │ • login() → calls Firebase + backend  │ │
│  │ • signOut()       │    │ • signup() → calls Firebase + backend │ │
│  │ • onAuthChanged() │───▶│ • logout() → clears state             │ │
│  │ • getIdToken()    │    │ • getToken() → returns ID token       │ │
│  └──────────────────┘    └────────────────────────────────────────┘ │
└─────────────────────────────────────┬───────────────────────────────┘
                                      │
                         Authorization: Bearer <id_token>
                                      │
┌─────────────────────────────────────┼───────────────────────────────┐
│                           BACKEND   │                               │
│                                     ▼                               │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                    Auth Middleware                               ││
│  │                                                                 ││
│  │  1. Extract token from Authorization header                     ││
│  │  2. firebase_admin.auth.verify_id_token(token)                  ││
│  │  3. Extract uid, email, name from decoded token                 ││
│  │  4. Look up user in SQLite by firebase_uid                      ││
│  │  5. Inject current_user into request                            ││
│  │                                                                 ││
│  │  On failure → 401 Unauthorized                                  ││
│  └─────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────┘
```

### 6.2 Signup Flow (Detailed)

```
1. User fills signup form (name, email, password, role)
2. Frontend calls Firebase Auth SDK:
   - firebase.auth().createUserWithEmailAndPassword(email, password)
   - firebase.auth().currentUser.updateProfile({ displayName: name })
3. Firebase creates user and returns ID token
4. Frontend sends POST /api/auth/register:
   - Body: { id_token, role }
5. Backend verifies ID token via Firebase Admin SDK
6. Backend creates user row in SQLite:
   - firebase_uid = decoded_token.uid
   - email = decoded_token.email
   - name = decoded_token.name
   - role = request.role
7. Backend returns user profile JSON
8. Frontend stores user in AuthContext
9. Frontend redirects to /dashboard
```

### 6.3 Login Flow (Detailed)

```
1. User enters email + password (or clicks Google Sign-In)
2. Frontend calls Firebase Auth SDK:
   - Email: firebase.auth().signInWithEmailAndPassword(email, password)
   - Google: firebase.auth().signInWithPopup(googleProvider)
3. Firebase returns ID token
4. Frontend sends POST /api/auth/login:
   - Body: { id_token }
5. Backend verifies token, looks up user by firebase_uid
6. If user not found (first Google login) → create user, prompt role selection
7. Backend updates last_login, returns user profile
8. Frontend stores user in AuthContext
9. Redirect to /dashboard
```

### 6.4 Token Verification Flow

```
Every authenticated API request:

1. Axios interceptor attaches:
   Authorization: Bearer <firebase_id_token>

2. Auth middleware on backend:
   - Extracts token from header
   - Calls firebase_admin.auth.verify_id_token(token)
   - This verifies:
     ✓ Token signature (signed by Google)
     ✓ Token expiry (1 hour default)
     ✓ Token issuer
     ✓ Token audience (matches Firebase project)
   - Extracts: uid, email, name, email_verified

3. If token expired:
   - Frontend Firebase SDK auto-refreshes tokens
   - Axios interceptor always calls getIdToken(true) for fresh token
   - No manual refresh logic needed

4. If verification fails:
   - Backend returns 401
   - Frontend redirects to /login
```

### 6.5 Protected Routes Flow (Frontend)

```jsx
// Conceptual flow (not actual code):

ProtectedRoute Component:
  1. Read user from AuthContext
  2. Read loading from AuthContext
  3. If loading → show LoadingSpinner
  4. If !user → redirect to /login (using React Router Navigate)
  5. If user → render children (the protected page)
```

### 6.6 Firebase Configuration

| Config Item | Where Stored | Used By |
|-------------|-------------|---------|
| Firebase Web Config (apiKey, authDomain, projectId) | `frontend/src/config/firebase.js` | Frontend Firebase SDK initialization |
| Firebase Service Account Key | `backend/.env` (path to JSON key file) | Backend Firebase Admin SDK initialization |
| Firebase Project ID | `backend/.env` | Backend Firebase Admin SDK |

**Security Note:** The Firebase Web Config is designed to be public (it's embedded in client-side code). Security is enforced by Firebase Security Rules and backend token verification, not by keeping the config secret.

---

## 7. RAG Architecture

### 7.1 RAG Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         RAG PIPELINE                                │
│                                                                     │
│  ┌─────────┐    ┌──────────┐    ┌──────────┐    ┌───────────────┐  │
│  │  Ingest │───▶│  Chunk   │───▶│  Embed   │───▶│ Store in      │  │
│  │  (Load  │    │  (Split  │    │  (Gemini │    │ ChromaDB      │  │
│  │  Docs)  │    │  Text)   │    │  Embed)  │    │               │  │
│  └─────────┘    └──────────┘    └──────────┘    └───────┬───────┘  │
│                                                         │          │
│                                                         │          │
│  ┌─────────┐    ┌──────────┐    ┌──────────┐    ┌───────┴───────┐  │
│  │ Generate│◀───│  Build   │◀───│ Retrieve │◀───│ Query         │  │
│  │ Response│    │  Prompt  │    │  Relevant │    │ ChromaDB      │  │
│  │ (Gemini)│    │  (Context│    │  Chunks  │    │               │  │
│  │         │    │  + Query)│    │          │    │               │  │
│  └─────────┘    └──────────┘    └──────────┘    └───────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### 7.2 Document Ingestion Pipeline

**Triggered by:** User file upload (Upload & Chat) OR one-time corpus seeding (Know Your Kanoon legal corpus).

**Legal Corpus Contents:**
- Constitution of India (all articles, schedules, amendments)
- Bharatiya Nyaya Sanhita (BNS) — replaces IPC
- Bharatiya Nagarik Suraksha Sanhita (BNSS) — replaces CrPC
- Bharatiya Sakshya Adhiniyam (BSA) — replaces Indian Evidence Act
- Selected important Central Acts (e.g., Right to Information Act, Consumer Protection Act, Hindu Marriage Act)
- Selected landmark Supreme Court judgments (e.g., Kesavananda Bharati, Maneka Gandhi, Vishaka)

**Corpus Strategy:** All corpus files are curated PDFs/text files stored in `backend/corpus/` directory. A one-time seed script (`python -m app.scripts.seed_corpus`) processes these files and populates the `legal_corpus` ChromaDB collection. No runtime scraping, no third-party APIs, no live web retrieval.

```
Step 1: Load Document
  ├── PDF → PyPDFLoader (extracts text page-by-page, preserves page numbers)
  ├── DOCX → Docx2txtLoader (extracts full text, preserves structure)
  └── TXT → TextLoader (reads raw text)

Step 2: Pre-process
  ├── Remove excessive whitespace
  ├── Normalize Unicode characters
  └── Preserve paragraph boundaries

Step 3: Output → List of Document objects with:
  ├── page_content: string (the text)
  └── metadata: { source, page_number, file_name }
```

### 7.3 Chunking Strategy

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| **Method** | `RecursiveCharacterTextSplitter` | Splits on natural boundaries (paragraphs, sentences, then characters) |
| **Chunk Size** | 1000 characters | Balances context completeness with retrieval precision |
| **Chunk Overlap** | 200 characters | Prevents loss of context at chunk boundaries |
| **Separators** | `["\n\n", "\n", ". ", " ", ""]` | Priority: paragraph → line → sentence → word → character |

**Why these values:**
- **1000 chars** ≈ 200-250 words ≈ 1-2 legal paragraphs. This is large enough to capture a complete legal clause or section, but small enough for precise retrieval.
- **200 char overlap** ensures that sentences split across chunk boundaries are present in at least one complete chunk.
- **RecursiveCharacterTextSplitter** is preferred over `CharacterTextSplitter` because it respects natural text boundaries.

### 7.4 Embedding Pipeline

| Component | Choice | Details |
|-----------|--------|---------|
| **Embedding Model** | Gemini `models/embedding-001` | Google's text embedding model, free tier available |
| **Dimensions** | 768 | Default dimension for Gemini embeddings |
| **Task Type** | `RETRIEVAL_DOCUMENT` for indexing, `RETRIEVAL_QUERY` for queries | Optimized for asymmetric search (short query vs. long passage) |

```
Indexing:
  chunks[] → embed(task="RETRIEVAL_DOCUMENT") → vectors[] → ChromaDB.add()

Querying:
  user_query → embed(task="RETRIEVAL_QUERY") → query_vector → ChromaDB.query()
```

### 7.5 Retrieval Pipeline

```
1. User sends a query (e.g., "What does Section 302 of BNS say about murder?")

2. Embed the query:
   query_vector = embed(query, task="RETRIEVAL_QUERY")

3. Query ChromaDB:
   results = collection.query(
       query_embeddings=[query_vector],
       n_results=5,              ← Top 5 most relevant chunks
       include=["documents", "metadatas", "distances"]
   )

4. Filter by relevance:
   - Discard results with distance > threshold (0.8)
   - This prevents injecting irrelevant context

5. Build context string:
   context = "\n---\n".join([
       f"[Source: {r.metadata.source}, Page: {r.metadata.page}]\n{r.document}"
       for r in results
   ])

6. Return context + metadata to the prompt builder
```

**Retrieval Parameters:**

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `n_results` | 5 | Sufficient context without overwhelming the LLM's context window |
| Distance metric | Cosine similarity (ChromaDB default) | Standard for text embeddings |
| Relevance threshold | 0.8 (distance) | Prevents injecting irrelevant chunks; tunable based on testing |

### 7.6 Citation Pipeline

Citations are extracted from the RAG context and structured for the frontend.

```
1. Retrieved chunks include metadata:
   { source: "Bharatiya Nyaya Sanhita", page: 42, section: "302" }

2. System prompt instructs Gemini to:
   - Reference sources using [Source: X, Section: Y] format
   - Only cite sources present in the provided context
   - Do NOT fabricate citations

3. Post-processing (backend):
   - Parse AI response for citation markers
   - Match citation markers to metadata from retrieved chunks
   - Structure citations as JSON array:
     [
       { "source": "Bharatiya Nyaya Sanhita", "section": "302", "relevance": "direct" },
       { "source": "Kesavananda Bharati v. State of Kerala", "year": "1973", "relevance": "supporting" }
     ]

4. Return citations alongside the response for frontend rendering
```

---

## 8. ChromaDB Design

### 8.1 Collection Strategy

ChromaDB uses **collections** (similar to database tables) to organize vectors. NYAAY AI uses two types of collections:

| Collection Type | Naming Pattern | Purpose | Lifecycle |
|----------------|---------------|---------|-----------|
| **Legal Corpus** | `legal_corpus` | Pre-loaded Indian legal texts for Know Your Kanoon and Counter Arguments | Persistent — created once during setup |
| **User Document** | `doc_{upload_id}` | Vectors for a specific user's uploaded document | Created on upload, deleted when user deletes upload |

### 8.2 Collection Schema

Each document stored in ChromaDB has:

```
{
  "id": "chunk_{uuid}",                    ← Unique chunk identifier
  "embedding": [0.123, -0.456, ...],       ← 768-dim Gemini embedding
  "document": "The text content...",        ← Original chunk text
  "metadata": {
    "source": "Bharatiya Nyaya Sanhita",   ← Document/Act name
    "category": "criminal_law",             ← Corpus category
    "page": 42,                             ← Page number (if applicable)
    "section": "302",                       ← Section number (if applicable)
    "chunk_index": 7,                       ← Position in original document
    "file_name": "bns_2023.pdf",            ← Original file name
    "user_id": "user_123"                   ← Owner (for user-uploaded docs)
  }
}
```

### 8.3 Storage Strategy

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| **Persistence** | Persistent mode (`chroma_db/` directory) | Data survives server restarts |
| **Storage Location** | `backend/chroma_db/` | Co-located with backend; simple file-based storage |
| **Index Type** | HNSW (ChromaDB default) | Good balance of speed and accuracy for MVP scale |
| **Distance Metric** | Cosine (`hnsw:space: cosine`) | Standard for text embeddings |
| **Max Collection Size** | No hard limit for MVP | Legal corpus: ~8K chunks; user docs: ~1K chunks each |

### 8.4 Data Isolation

- **Legal corpus** collection: Shared across all users (read-only after initial seeding).
- **User document** collections: Isolated per upload. Collection name includes the upload ID, and queries are always scoped to the specific collection.
- **No cross-user data leakage**: A user's uploaded document vectors are never queried by another user. Per-document collections make this structurally impossible.

### 8.5 ChromaDB Design Decision

**Chosen: Per-Document Collections over Shared Collection with Metadata Filtering.**

| Criterion | Per-Document Collections ✅ | Shared Collection |
|-----------|:------------------------:|:------------------:|
| **Data Isolation** | Perfect — structurally impossible to leak | Relies on correct `where` clause |
| **Query Simplicity** | `collection.query(query)` — no filters | Must add `where={"upload_id": id}` always |
| **Security Risk** | Zero cross-user risk | Bug in filter = data leakage |
| **Cleanup** | Drop collection | Delete by metadata filter |
| **Scalability** | ⚠️ Many small HNSW indexes | ✅ Single large index |
| **MVP Fit** | ✅ Simpler, safer | ⚠️ More code, more risk |

**Rationale:** For a legal platform handling sensitive documents, structural data isolation is worth the scalability tradeoff. At MVP scale (< 1000 collections), ChromaDB handles per-document collections well.

---

## 9. Folder Structure

### 9.1 Complete Frontend Structure

```
FRONTEND/
├── public/
│   ├── index.html
│   ├── favicon.ico
│   └── assets/
│       └── images/                    ← Static images (logo, icons)
│
├── src/
│   ├── main.jsx                       ← Entry point, renders App
│   ├── App.jsx                        ← Router setup, context providers
│   │
│   ├── config/
│   │   └── firebase.js                ← Firebase app initialization
│   │
│   ├── contexts/
│   │   ├── AuthContext.jsx            ← Authentication state + methods
│   │   └── ThemeContext.jsx           ← Light/dark theme state
│   │
│   ├── layouts/
│   │   ├── PublicLayout.jsx           ← Layout for landing, auth pages
│   │   └── DashboardLayout.jsx        ← Sidebar + TopBar + content area
│   │
│   ├── pages/
│   │   ├── LandingPage.jsx
│   │   ├── LoginPage.jsx
│   │   ├── SignupPage.jsx
│   │   ├── DashboardPage.jsx
│   │   ├── KnowKanoonPage.jsx
│   │   ├── UploadChatPage.jsx
│   │   ├── DocHubPage.jsx
│   │   ├── DocHubGeneratePage.jsx
│   │   ├── CounterArgumentPage.jsx
│   │   ├── ProfilePage.jsx
│   │   ├── ChatHistoryPage.jsx
│   │   └── ChatDetailPage.jsx
│   │
│   ├── components/
│   │   ├── common/
│   │   │   ├── Navbar.jsx             ← Public navigation bar
│   │   │   ├── Sidebar.jsx            ← Dashboard sidebar navigation
│   │   │   ├── TopBar.jsx             ← User info + logout in dashboard
│   │   │   ├── LoadingSpinner.jsx
│   │   │   ├── EmptyState.jsx
│   │   │   ├── Toast.jsx
│   │   │   ├── Modal.jsx
│   │   │   └── ProtectedRoute.jsx     ← Auth guard wrapper
│   │   │
│   │   ├── chat/
│   │   │   ├── ChatWindow.jsx         ← Scrollable message list
│   │   │   ├── ChatBubble.jsx         ← Single message bubble
│   │   │   ├── ChatInput.jsx          ← Text input + send button
│   │   │   ├── ChatSidebar.jsx        ← Conversation list panel
│   │   │   └── CitationPanel.jsx      ← Source references display
│   │   │
│   │   ├── upload/
│   │   │   ├── FileUploader.jsx       ← Drag-and-drop upload zone
│   │   │   └── ProcessingIndicator.jsx← Upload/parsing progress
│   │   │
│   │   ├── dochub/
│   │   │   ├── TemplateCard.jsx       ← Template selection card
│   │   │   ├── DynamicForm.jsx        ← Template-specific input form
│   │   │   ├── DocumentPreview.jsx    ← Generated doc preview
│   │   │   └── ExportButtons.jsx      ← PDF/DOCX download buttons
│   │   │
│   │   ├── counter/
│   │   │   ├── ArgumentInput.jsx      ← Legal argument text input
│   │   │   └── CounterArgumentResults.jsx ← Categorized results display
│   │   │
│   │   ├── dashboard/
│   │   │   ├── FeatureCard.jsx        ← Feature navigation card
│   │   │   ├── RecentActivity.jsx     ← Recent interactions list
│   │   │   └── WelcomeBanner.jsx      ← Personalized greeting
│   │   │
│   │   └── profile/
│   │       ├── ProfileForm.jsx        ← Edit profile form
│   │       └── PreferencesForm.jsx    ← Theme + settings
│   │
│   ├── services/
│   │   ├── api.js                     ← Axios instance + interceptors
│   │   ├── authService.js
│   │   ├── chatService.js
│   │   ├── uploadService.js
│   │   ├── docService.js
│   │   ├── counterArgService.js
│   │   ├── profileService.js
│   │   └── historyService.js
│   │
│   ├── utils/
│   │   ├── constants.js               ← App-wide constants
│   │   ├── formatters.js              ← Date, text formatting helpers
│   │   └── validators.js              ← Form validation helpers
│   │
│   └── styles/
│       └── index.css                  ← Tailwind directives + custom CSS
│
├── tailwind.config.js
├── postcss.config.js
├── vite.config.js
├── package.json
└── .env                               ← VITE_API_URL, Firebase config
```

### 9.2 Complete Backend Structure

```
BACKEND/
├── app/
│   ├── main.py                        ← FastAPI app creation, middleware, router mounting, rate limiter setup
│   ├── config.py                      ← Environment variables, settings (via pydantic-settings)
│   │
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth.py                    ← Firebase token verification dependency
│   │   └── error_handler.py           ← Global exception handlers (no stack traces in production)
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth_routes.py             ← POST /register, POST /login
│   │   ├── chat_routes.py             ← POST /send, GET /conversations, GET/DELETE /:id
│   │   ├── upload_routes.py           ← POST /upload, POST /chat, GET /list
│   │   ├── doc_routes.py              ← GET /templates, POST /generate, POST /export
│   │   ├── counter_routes.py          ← POST /generate, POST /save
│   │   ├── profile_routes.py          ← GET /, PUT /update
│   │   └── history_routes.py          ← GET /, GET /search, DELETE /:id
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── chat_service.py
│   │   ├── upload_service.py
│   │   ├── doc_service.py
│   │   ├── counter_service.py
│   │   ├── profile_service.py
│   │   └── history_service.py
│   │
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── gemini_client.py           ← Gemini API wrapper (init, generate, embed, retry, timeout)
│   │   ├── rag_service.py             ← Full RAG pipeline orchestration
│   │   ├── retriever.py               ← ChromaDB query + ranking
│   │   ├── chunking.py                ← Text splitting logic
│   │   ├── embedding_service.py       ← Gemini embedding wrapper
│   │   └── prompts/
│   │       ├── know_kanoon_system.txt
│   │       ├── upload_chat_system.txt
│   │       ├── doc_gen_system.txt
│   │       ├── counter_arg_system.txt
│   │       └── templates/
│   │           ├── affidavit.txt
│   │           ├── rental_agreement.txt
│   │           └── legal_notice.txt
│   │
│   ├── file_processing/
│   │   ├── __init__.py
│   │   ├── file_parser.py             ← Dispatcher: extension → parser + validation pipeline
│   │   ├── pdf_parser.py
│   │   ├── docx_parser.py
│   │   ├── txt_parser.py
│   │   ├── pdf_exporter.py            ← Generate PDF from content
│   │   └── docx_exporter.py           ← Generate DOCX from content
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py              ← SQLite connection + setup (WAL mode)
│   │   ├── models.py                  ← Table definitions (dataclasses or Pydantic)
│   │   └── migrations/
│   │       └── 001_initial_schema.sql ← Initial table creation SQL
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth_schemas.py            ← Request/response Pydantic models
│   │   ├── chat_schemas.py
│   │   ├── upload_schemas.py
│   │   ├── doc_schemas.py
│   │   ├── counter_schemas.py
│   │   └── profile_schemas.py
│   │
│   └── scripts/
│       └── seed_corpus.py             ← One-time legal corpus seeding script
│
├── corpus/                             ← Curated legal corpus files
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
│
├── chroma_db/                          ← ChromaDB persistent storage
│   └── (auto-generated files)
│
├── uploads/                            ← User uploaded files
│   └── {user_id}/
│       └── {upload_id}_{filename}
│
├── exports/                            ← Generated document exports
│   └── {user_id}/
│       └── {doc_id}.{pdf|docx}
│
├── requirements.txt                    ← Python dependencies
├── .env                                ← API keys, Firebase config path, DB path
└── .env.example                        ← Template for .env (no secrets)
```

### 9.3 Project Root Structure

```
NYAAY AI/
├── FRONTEND/                           ← React SPA (Vite)
├── BACKEND/                            ← FastAPI server
├── ASSETS/                             ← Shared assets (logos, design files)
├── DOCS/
│   ├── PRD_v2.md                       ← ✅ Approved
│   ├── ARCHITECTURE_v2.md              ← ✅ This document
│   ├── DATABASE_SCHEMA.md
│   ├── ROUTES.md
│   ├── API_SPEC.md
│   ├── RAG_ARCHITECTURE.md
│   ├── SECURITY.md
│   ├── TASKS.md
│   └── DECISIONS.md
└── .gitignore
```

---

## 10. Deployment Architecture

### 10.1 Local Development Setup

```
Terminal 1 (Frontend):
  cd FRONTEND
  npm install
  npm run dev                          ← Vite dev server on http://localhost:5173

Terminal 2 (Backend):
  cd BACKEND
  pip install -r requirements.txt
  uvicorn app.main:app --reload        ← FastAPI dev server on http://localhost:8000

External Services:
  Firebase Auth                        ← Cloud (Google managed)
  Gemini API                           ← Cloud (Google managed)

Local Services:
  SQLite                               ← File: backend/nyaay.db
  ChromaDB                             ← Directory: backend/chroma_db/
```

**Development Environment Requirements:**

| Tool | Version | Purpose |
|------|---------|---------|
| Node.js | 18+ | Frontend runtime |
| npm | 9+ | Frontend package manager |
| Python | 3.10+ | Backend runtime |
| pip | 23+ | Python package manager |
| Git | 2.40+ | Version control |

### 10.2 MVP Deployment Strategy

For MVP, the simplest viable deployment:

```
┌──────────────────────────────────────────────┐
│           Single VPS / Cloud VM              │
│           (e.g., Railway, Render)             │
│                                              │
│  ┌────────────────┐  ┌────────────────────┐  │
│  │  Vite Build    │  │   FastAPI Server   │  │
│  │  (Static Files)│  │   (Uvicorn)        │  │
│  │  Served by     │  │                    │  │
│  │  FastAPI or    │  │   SQLite + ChromaDB│  │
│  │  Nginx         │  │   (Embedded)       │  │
│  └────────────────┘  └────────────────────┘  │
└──────────────────────────────────────────────┘
```

**MVP deployment is simple:**
1. Build frontend: `npm run build` → produces `dist/` static files.
2. Serve static files from FastAPI (or place behind Nginx).
3. Run FastAPI with Uvicorn on a single process.
4. SQLite and ChromaDB run embedded — no separate database servers.

### 10.3 Future Scaling Plan (Post-MVP)

```
Phase 2 Deployment:
┌────────────┐     ┌────────────┐     ┌────────────┐
│   Vercel   │     │  Railway   │     │ Managed    │
│ (Frontend) │────▶│  (Backend) │────▶│ PostgreSQL │
│  CDN +     │     │  FastAPI   │     │            │
│  Static    │     │  + Docker  │     │            │
└────────────┘     └────────────┘     └────────────┘
                         │
                    ┌────┴────┐
                    │ Managed │
                    │ ChromaDB│
                    │ (Cloud) │
                    └─────────┘
```

**Scaling triggers and actions:**

| Trigger | Action |
|---------|--------|
| SQLite write contention | Migrate to PostgreSQL |
| ChromaDB dataset > 1M vectors | Move to managed Pinecone or Weaviate |
| > 100 concurrent users | Add Gunicorn workers or container replicas |
| File storage > 50GB | Migrate to S3/GCS |
| Need CI/CD | Add GitHub Actions pipeline |

---

## 11. Security Considerations

> **Note:** For the full security design including prompt injection defense, RAG poisoning prevention, file upload security, and logging strategy, see [SECURITY.md](./SECURITY.md).

### 11.1 Authentication Security

| Concern | Mitigation |
|---------|-----------|
| Token forgery | Firebase ID tokens are signed by Google. Backend verifies signature via Firebase Admin SDK — cannot be forged. |
| Token expiry | Firebase ID tokens expire after 1 hour. Frontend SDK auto-refreshes. Backend rejects expired tokens. |
| API key exposure | Gemini API key and Firebase Admin credentials stored in backend `.env` — never exposed to frontend. |
| Firebase Web Config exposure | Intentional — Firebase Web Config is designed to be public. Security comes from Firebase Rules + backend verification, not config secrecy. |

### 11.2 Data Security

| Concern | Mitigation |
|---------|-----------|
| Cross-user data access | All database queries filter by `user_id`. API middleware injects `current_user` — no user ID is accepted from the client. |
| SQL injection | Use parameterized queries exclusively. Never use string interpolation for SQL. |
| File upload attacks | 5-step validation pipeline: extension check, MIME type check (python-magic), size limit (10MB), page count (300), content extraction test. Store files outside web root. |
| Path traversal | Sanitize filenames. Use UUID-based storage paths, never user-provided filenames for storage. |

### 11.3 API Security

| Concern | Mitigation |
|---------|-----------|
| CORS | Restrict allowed origins to frontend URL (`localhost:5173` in dev, production domain in prod). |
| Rate limiting | Implemented using `slowapi`. Per-user limits: 20 req/min (chat), 10 req/min (upload, docgen, counter), 5 req/min (auth). See Rate Limiting Design section. |
| Input validation | Pydantic models validate all request bodies. Reject unexpected fields. |
| Error information leakage | Global error handler returns generic messages. Stack traces only in development mode. |

### 11.4 AI Security

| Concern | Mitigation |
|---------|-----------|
| Prompt injection | System prompts are hardcoded on backend. User input is clearly delimited in the prompt template with markers. Input/output boundary enforcement. |
| Sensitive data in prompts | Uploaded document content is sent to Gemini API. Users are informed in Terms of Service. No PII is logged. |
| Hallucinated legal citations | RAG grounding + system prompt instructions to only cite from provided context. Disclaimers on all outputs. |
| RAG poisoning | Per-document collections prevent cross-user contamination. Legal corpus is read-only after seeding. |

### 11.5 Rate Limiting Design

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

---

## 12. Architecture Decisions Log

| # | Decision | Options Considered | Chosen | Rationale |
|---|----------|-------------------|--------|-----------|
| 1 | **Monolithic backend** | Monolith vs. Microservices | Monolith | Single FastAPI server. Simplest possible deployment. One codebase, one process, one log. Microservices add network overhead, deployment complexity, and distributed debugging — all unnecessary for MVP. |
| 2 | **Embedded ChromaDB** | Embedded vs. Client-Server ChromaDB vs. Pinecone | Embedded | Runs in the same Python process. Zero network latency for vector queries. No separate server to manage. Sufficient for MVP scale (~8K legal corpus chunks + per-user document chunks). |
| 3 | **SQLite with raw SQL** | SQLite + raw SQL vs. SQLite + SQLAlchemy ORM vs. PostgreSQL | SQLite + raw SQL | ORM adds abstraction overhead for 6 simple tables. Raw parameterized SQL is easier to debug and learn. SQLite needs no server. Migration to PostgreSQL + SQLAlchemy is a clean Phase 2 task. |
| 4 | **React Context over Redux** | React Context vs. Redux vs. Zustand | React Context | Only two pieces of global state: auth user and theme. No complex state transitions, no shared state across unrelated components. Context is built-in, zero dependencies, and sufficient for this scale. |
| 5 | **Vite over CRA** | Vite vs. Create React App | Vite | CRA is deprecated/unmaintained. Vite is the community standard: faster builds, faster HMR, better developer experience, actively maintained. |
| 6 | **Separate prompt files** | Prompts as Python strings vs. Separate .txt files | Separate files | Prompts are configuration, not code. Separate files make prompts: (a) version-controllable with meaningful diffs, (b) editable by non-engineers, (c) swappable without code changes. |
| 7 | **Per-document ChromaDB collections** | Single collection with metadata filtering vs. Per-document collections | Per-document collections | Upload & Chat must scope queries to a specific document. Separate collections guarantee perfect isolation with zero risk of cross-document contamination. Collection overhead is negligible for MVP. |
| 8 | **Server-side disclaimers** | Client-side vs. Server-side disclaimer injection | Server-side | Disclaimers appended by the backend cannot be bypassed by a modified frontend. This is a legal compliance measure — the AI output is never served without a disclaimer. |
| 9 | **No WebSocket for chat** | REST polling vs. WebSocket vs. SSE | REST (synchronous) | MVP chat is request-response (user sends message → waits → gets AI response). No real-time streaming needed. WebSocket adds complexity for zero user benefit at MVP scale. Streaming can be added later via SSE. |
| 10 | **Local file storage** | Local filesystem vs. S3 vs. Firebase Storage | Local filesystem | Zero cost, zero configuration, zero network latency. Files stored in `uploads/` and `exports/` directories. Sufficient for single-server MVP. Clear migration path to S3/GCS when needed. |
| 11 | **UUID for entity IDs** | Auto-increment integers vs. UUIDs | Hybrid | `users` table uses auto-increment (simple, internal-only). `conversations`, `documents`, `uploads`, `counter_arguments` use UUIDs (exposed in URLs, prevents enumeration attacks). |
| 12 | **Gemini for both LLM and embeddings** | Gemini LLM + Gemini Embed vs. Gemini LLM + OpenAI Embed | Gemini for both | Single API key, single billing, single SDK. Gemini's embedding model is free-tier eligible and produces quality embeddings. No reason to split across providers for MVP. |
| 13 | **Curated legal corpus** | Live scraping vs. API-based vs. Curated files | Curated files | No legal API access for students, scraping is legally grey and unreliable, curated files are controllable and high-quality. Constitution + BNS/BNSS/BSA + selected acts + landmark cases provides sufficient MVP coverage. |
| 14 | **slowapi rate limiting** | No rate limiting vs. slowapi vs. custom middleware | slowapi | Simple integration with FastAPI, per-user and per-IP support, in-memory storage sufficient for MVP. Prevents Gemini API abuse. |
| 15 | **3 DocHub templates** | 5 templates vs. 3 templates | 3 templates | NDA and Power of Attorney are complex legal documents that require more template refinement. Legal Notice, Rental Agreement, and Affidavit are more commonly needed and simpler to template. Reduces scope without reducing demo value. Move NDA and PoA to Phase 2. |
| 16 | **3 user roles** | 4 roles (incl. Researcher) vs. 3 roles | 3 roles (Citizen, Student, Lawyer) | Researcher role was functionally identical to Student in MVP — same features, same permissions. Adding it created unnecessary complexity in role selection UI and role-based logic. Can be re-added in Phase 2 if distinct features are designed. |

---

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

**Mitigation:** Legal corpus: ~8K chunks × 768 dims × 4 bytes ≈ 24MB. Per-user documents: ~500 chunks each. At 100 users with 5 uploads each, that's ~500 collections × 500 chunks = 250K chunks ≈ 750MB. Manageable on a 2GB+ server.

**Escalation:** Move to ChromaDB client-server mode or Pinecone when vector count exceeds 1M.

### 13.4 File Storage Growth

**Risk:** Local filesystem stores uploads and exports. No automatic cleanup.

**Mitigation:** 10MB per upload × 100 users × 10 uploads = 10GB. Manageable for MVP. Add a cleanup script for orphaned files.

**Escalation:** Migrate to S3/GCS with lifecycle policies.

### 13.5 Gemini API Cost

**Risk:** As usage grows, Gemini API costs could become significant. Each chat message, document generation, and counter-argument requires an API call.

**Mitigation:** Free tier handles ~1,500 requests/day. Rate limiting (20 req/min per user for chat) prevents abuse. Monitor usage via logging.

**Escalation:** Implement usage quotas per user, add caching for common queries.

---

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

---

> **Next Step:** This Architecture document is approved. Proceed to implementation using [TASKS.md](./TASKS.md) and [API_SPEC.md](./API_SPEC.md).
