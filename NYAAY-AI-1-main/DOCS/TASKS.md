# NYAAY AI — Implementation Tasks

> **Version:** 1.0
> **Date:** 2026-06-23
> **Author:** Ansh Darji
> **Status:** Final
> **Total Sprints:** 6 (1 week each)
> **Estimated Completion:** 6 weeks

---

## Sprint 1: Foundation & Authentication

**Goal:** User can sign up, log in (email + Google), and see an empty dashboard.

### Frontend Tasks

| # | Task | Component/File | Priority |
|---|------|---------------|:--------:|
| F1.1 | Initialize Vite + React project | `FRONTEND/` scaffolding | P0 |
| F1.2 | Install dependencies (react-router, axios, tailwindcss, firebase) | `package.json` | P0 |
| F1.3 | Configure Tailwind CSS + PostCSS | `tailwind.config.js`, `postcss.config.js` | P0 |
| F1.4 | Set up Firebase config | `src/config/firebase.js` | P0 |
| F1.5 | Create AuthContext (user state, login, signup, logout, getToken) | `src/contexts/AuthContext.jsx` | P0 |
| F1.6 | Create ProtectedRoute component | `src/components/common/ProtectedRoute.jsx` | P0 |
| F1.7 | Create PublicLayout (Navbar + children) | `src/layouts/PublicLayout.jsx` | P0 |
| F1.8 | Create DashboardLayout (Sidebar + TopBar + children) | `src/layouts/DashboardLayout.jsx` | P0 |
| F1.9 | Create Navbar component | `src/components/common/Navbar.jsx` | P0 |
| F1.10 | Create Sidebar component (feature nav links) | `src/components/common/Sidebar.jsx` | P0 |
| F1.11 | Create TopBar component (user info + logout) | `src/components/common/TopBar.jsx` | P0 |
| F1.12 | Create LoginPage (email/password + Google Sign-In) | `src/pages/LoginPage.jsx` | P0 |
| F1.13 | Create SignupPage (name, email, password, role selector) | `src/pages/SignupPage.jsx` | P0 |
| F1.14 | Create DashboardPage (empty state / placeholder) | `src/pages/DashboardPage.jsx` | P1 |
| F1.15 | Set up React Router (App.jsx) with all routes | `src/App.jsx` | P0 |
| F1.16 | Set up Axios instance with auth interceptor | `src/services/api.js` | P0 |
| F1.17 | Create authService (register, login API calls) | `src/services/authService.js` | P0 |
| F1.18 | Create LoadingSpinner component | `src/components/common/LoadingSpinner.jsx` | P1 |
| F1.19 | Create Toast notification component | `src/components/common/Toast.jsx` | P1 |

### Backend Tasks

| # | Task | File | Priority |
|---|------|------|:--------:|
| B1.1 | Initialize FastAPI project structure | `BACKEND/app/` scaffolding | P0 |
| B1.2 | Create requirements.txt (fastapi, uvicorn, firebase-admin, python-dotenv, pydantic) | `requirements.txt` | P0 |
| B1.3 | Create config.py (environment variables via pydantic-settings) | `app/config.py` | P0 |
| B1.4 | Create main.py (app init, CORS, router mounting) | `app/main.py` | P0 |
| B1.5 | Set up Firebase Admin SDK initialization | `app/config.py` | P0 |
| B1.6 | Create auth middleware (Firebase token verification) | `app/middleware/auth.py` | P0 |
| B1.7 | Create global error handler middleware | `app/middleware/error_handler.py` | P1 |
| B1.8 | Create SQLite database connection + setup | `app/database/connection.py` | P0 |
| B1.9 | Create initial schema SQL (all 6 tables) | `app/database/migrations/001_initial_schema.sql` | P0 |
| B1.10 | Create auth routes (POST /register, POST /login, GET /me) | `app/routes/auth_routes.py` | P0 |
| B1.11 | Create auth service (register user, login user, get user) | `app/services/auth_service.py` | P0 |
| B1.12 | Create auth schemas (Pydantic request/response models) | `app/schemas/auth_schemas.py` | P0 |
| B1.13 | Create .env.example with all required variables | `.env.example` | P0 |

### Testing

- [ ] Email signup → login → dashboard redirect works
- [ ] Google Sign-In → login → dashboard redirect works
- [ ] Protected routes redirect to /login when unauthenticated
- [ ] Token verification on backend (valid token → 200, invalid → 401)
- [ ] Firebase error handling (duplicate email, weak password)

### Deliverable
> **User can sign up (email or Google), log in, see empty dashboard, and log out.**

### Dependencies & Blockers
- 🔒 Firebase project must be created and configured
- 🔒 Firebase service account key JSON downloaded
- 🔒 Firebase web config values obtained

---

## Sprint 2: Dashboard & Know Your Kanoon

**Goal:** User can ask legal questions and get AI-powered responses with citations.

### Frontend Tasks

| # | Task | Component/File | Priority |
|---|------|---------------|:--------:|
| F2.1 | Create WelcomeBanner component (greeting + user name) | `src/components/dashboard/WelcomeBanner.jsx` | P0 |
| F2.2 | Create FeatureCard component (icon, title, description, link) | `src/components/dashboard/FeatureCard.jsx` | P0 |
| F2.3 | Create RecentActivity component (placeholder/empty state) | `src/components/dashboard/RecentActivity.jsx` | P1 |
| F2.4 | Complete DashboardPage (wire up components) | `src/pages/DashboardPage.jsx` | P0 |
| F2.5 | Create EmptyState component | `src/components/common/EmptyState.jsx` | P1 |
| F2.6 | Create ChatWindow component (scrollable message list) | `src/components/chat/ChatWindow.jsx` | P0 |
| F2.7 | Create ChatBubble component (user vs AI styling, markdown support) | `src/components/chat/ChatBubble.jsx` | P0 |
| F2.8 | Create ChatInput component (textarea + send button) | `src/components/chat/ChatInput.jsx` | P0 |
| F2.9 | Create ChatSidebar component (conversation list) | `src/components/chat/ChatSidebar.jsx` | P0 |
| F2.10 | Create CitationPanel component (source references) | `src/components/chat/CitationPanel.jsx` | P1 |
| F2.11 | Create KnowKanoonPage (chat layout with sidebar) | `src/pages/KnowKanoonPage.jsx` | P0 |
| F2.12 | Create chatService (create conversation, send message, list, get, delete) | `src/services/chatService.js` | P0 |

### Backend Tasks

| # | Task | File | Priority |
|---|------|------|:--------:|
| B2.1 | Create Gemini client wrapper (init, generate, embed, retry, timeout) | `app/ai/gemini_client.py` | P0 |
| B2.2 | Create chunking module | `app/ai/chunking.py` | P0 |
| B2.3 | Create embedding service | `app/ai/embedding_service.py` | P0 |
| B2.4 | Create RAG service (full pipeline orchestration) | `app/ai/rag_service.py` | P0 |
| B2.5 | Create retriever (ChromaDB query + ranking) | `app/ai/retriever.py` | P0 |
| B2.6 | Initialize ChromaDB persistent client | `app/ai/rag_service.py` | P0 |
| B2.7 | Create Know Your Kanoon system prompt | `app/ai/prompts/know_kanoon_system.txt` | P0 |
| B2.8 | Create corpus seed script | `app/scripts/seed_corpus.py` | P0 |
| B2.9 | Prepare initial legal corpus files (Constitution + BNS at minimum) | `backend/corpus/` | P0 |
| B2.10 | Create chat routes (create conversation, send message, list, get, delete) | `app/routes/chat_routes.py` | P0 |
| B2.11 | Create chat service (conversation CRUD, message handling, AI orchestration) | `app/services/chat_service.py` | P0 |
| B2.12 | Create chat schemas (Pydantic models) | `app/schemas/chat_schemas.py` | P0 |

### Testing

- [ ] Seed corpus script runs successfully
- [ ] ChromaDB contains expected number of chunks
- [ ] User can create a conversation and send a message
- [ ] AI responds with relevant legal information
- [ ] Citations are present in AI responses
- [ ] Conversation persistence works (reload page, messages still there)
- [ ] Disclaimer appears on every AI response

### Deliverable
> **User can ask "What does Section 302 of BNS say?" and get a grounded AI response with citations.**

### Dependencies & Blockers
- 🔒 Gemini API key must be obtained
- 🔒 At least 2 legal corpus files must be prepared (Constitution of India, BNS)
- 🔗 Depends on: Sprint 1 (auth, database, project structure)

---

## Sprint 3: Upload & Chat

**Goal:** User can upload a PDF/DOCX/TXT and chat about its contents.

### Frontend Tasks

| # | Task | Component/File | Priority |
|---|------|---------------|:--------:|
| F3.1 | Create FileUploader component (drag-and-drop + file picker) | `src/components/upload/FileUploader.jsx` | P0 |
| F3.2 | Create ProcessingIndicator component (upload/parsing progress) | `src/components/upload/ProcessingIndicator.jsx` | P0 |
| F3.3 | Create UploadChatPage (upload zone → chat interface) | `src/pages/UploadChatPage.jsx` | P0 |
| F3.4 | Create uploadService (upload file, chat, list, delete) | `src/services/uploadService.js` | P0 |
| F3.5 | Add file upload validation on frontend (type, size) | `src/utils/validators.js` | P1 |
| F3.6 | Show upload history list (previous uploads) | `src/pages/UploadChatPage.jsx` | P1 |

### Backend Tasks

| # | Task | File | Priority |
|---|------|------|:--------:|
| B3.1 | Create file parser dispatcher (extension → parser) | `app/file_processing/file_parser.py` | P0 |
| B3.2 | Create PDF parser (PyPDFLoader) | `app/file_processing/pdf_parser.py` | P0 |
| B3.3 | Create DOCX parser (Docx2txtLoader) | `app/file_processing/docx_parser.py` | P0 |
| B3.4 | Create TXT parser (TextLoader) | `app/file_processing/txt_parser.py` | P0 |
| B3.5 | Create upload validation pipeline (extension, MIME, size, pages, content) | `app/file_processing/file_parser.py` | P0 |
| B3.6 | Create upload routes (upload file, chat, list, delete) | `app/routes/upload_routes.py` | P0 |
| B3.7 | Create upload service (save file, process, create collection, chat) | `app/services/upload_service.py` | P0 |
| B3.8 | Create Upload & Chat system prompt | `app/ai/prompts/upload_chat_system.txt` | P0 |
| B3.9 | Create upload schemas (Pydantic models) | `app/schemas/upload_schemas.py` | P0 |
| B3.10 | Implement per-document ChromaDB collection creation | `app/services/upload_service.py` | P0 |
| B3.11 | Implement collection cleanup on upload deletion | `app/services/upload_service.py` | P1 |

### Testing

- [ ] Upload a PDF → text extraction succeeds → status = 'ready'
- [ ] Upload a DOCX → text extraction succeeds
- [ ] Upload a TXT → text extraction succeeds
- [ ] Reject file > 10 MB
- [ ] Reject non-supported file types
- [ ] Reject PDF > 300 pages
- [ ] Chat with uploaded document returns relevant answers
- [ ] Answers reference specific pages/sections from the uploaded document
- [ ] Delete upload removes file, DB record, and ChromaDB collection

### Deliverable
> **User uploads a rental agreement PDF and asks "What are the termination clauses?" — gets a specific, cited answer.**

### Dependencies & Blockers
- 🔗 Depends on: Sprint 2 (RAG pipeline, Gemini client, ChromaDB)
- 📦 Required libraries: PyPDF2, python-docx, python-magic

---

## Sprint 4: DocHub

**Goal:** User can generate and export legal documents from templates.

### Frontend Tasks

| # | Task | Component/File | Priority |
|---|------|---------------|:--------:|
| F4.1 | Create TemplateCard component (template selection) | `src/components/dochub/TemplateCard.jsx` | P0 |
| F4.2 | Create DynamicForm component (renders fields from template config) | `src/components/dochub/DynamicForm.jsx` | P0 |
| F4.3 | Create DocumentPreview component (rendered document view) | `src/components/dochub/DocumentPreview.jsx` | P0 |
| F4.4 | Create ExportButtons component (PDF + DOCX download) | `src/components/dochub/ExportButtons.jsx` | P0 |
| F4.5 | Create DocHubPage (template selection grid) | `src/pages/DocHubPage.jsx` | P0 |
| F4.6 | Create DocHubGeneratePage (form → preview → export) | `src/pages/DocHubGeneratePage.jsx` | P0 |
| F4.7 | Create docService (templates, generate, export, list, get, delete) | `src/services/docService.js` | P0 |

### Backend Tasks

| # | Task | File | Priority |
|---|------|------|:--------:|
| B4.1 | Create Legal Notice template prompt | `app/ai/prompts/templates/legal_notice.txt` | P0 |
| B4.2 | Create Rental Agreement template prompt | `app/ai/prompts/templates/rental_agreement.txt` | P0 |
| B4.3 | Create Affidavit template prompt | `app/ai/prompts/templates/affidavit.txt` | P0 |
| B4.4 | Create DocHub system prompt | `app/ai/prompts/doc_gen_system.txt` | P0 |
| B4.5 | Create document routes (templates, generate, export, list, get, delete) | `app/routes/doc_routes.py` | P0 |
| B4.6 | Create document service (template config, AI generation, save) | `app/services/doc_service.py` | P0 |
| B4.7 | Create PDF exporter (reportlab or weasyprint) | `app/file_processing/pdf_exporter.py` | P0 |
| B4.8 | Create DOCX exporter (python-docx) | `app/file_processing/docx_exporter.py` | P0 |
| B4.9 | Create document schemas (Pydantic models) | `app/schemas/doc_schemas.py` | P0 |

### Testing

- [ ] Template list returns 3 templates with correct fields
- [ ] Generate Legal Notice with valid fields → well-formatted document
- [ ] Generate Rental Agreement → correct legal structure
- [ ] Generate Affidavit → proper sworn statement format
- [ ] Export as PDF → valid, downloadable PDF
- [ ] Export as DOCX → valid, downloadable DOCX
- [ ] Generated documents saved to database
- [ ] Invalid fields rejected with clear error

### Deliverable
> **User selects "Legal Notice", fills in the form, generates document, previews it, and exports as PDF.**

### Dependencies & Blockers
- 🔗 Depends on: Sprint 2 (Gemini client)
- 📦 Required libraries: reportlab or weasyprint, python-docx

---

## Sprint 5: Counter Arguments & Chat History

**Goal:** All core features functional. Counter-arguments work, chat history is browsable.

### Frontend Tasks

| # | Task | Component/File | Priority |
|---|------|---------------|:--------:|
| F5.1 | Create ArgumentInput component (large text input for legal argument) | `src/components/counter/ArgumentInput.jsx` | P0 |
| F5.2 | Create CounterArgumentResults component (4-category display) | `src/components/counter/CounterArgumentResults.jsx` | P0 |
| F5.3 | Create CounterArgumentPage (input → results) | `src/pages/CounterArgumentPage.jsx` | P0 |
| F5.4 | Create counterArgService (generate, list, get, delete) | `src/services/counterArgService.js` | P0 |
| F5.5 | Create ChatHistoryPage (list all chats, search, delete) | `src/pages/ChatHistoryPage.jsx` | P0 |
| F5.6 | Create ChatDetailPage (resume a previous conversation) | `src/pages/ChatDetailPage.jsx` | P0 |
| F5.7 | Create historyService (list, search, delete) | `src/services/historyService.js` | P0 |
| F5.8 | Wire up RecentActivity on Dashboard (real data) | `src/components/dashboard/RecentActivity.jsx` | P1 |

### Backend Tasks

| # | Task | File | Priority |
|---|------|------|:--------:|
| B5.1 | Create Counter Argument system prompt | `app/ai/prompts/counter_arg_system.txt` | P0 |
| B5.2 | Create counter routes (generate, list, get, delete) | `app/routes/counter_routes.py` | P0 |
| B5.3 | Create counter service (RAG query + Gemini generation, save) | `app/services/counter_service.py` | P0 |
| B5.4 | Create counter schemas (Pydantic models) | `app/schemas/counter_schemas.py` | P0 |
| B5.5 | Create history routes (list all, search, delete) | `app/routes/history_routes.py` | P0 |
| B5.6 | Create history service (unified query across tables) | `app/services/history_service.py` | P0 |

### Testing

- [ ] Submit a legal argument → receive 4 categories of counter-arguments
- [ ] Counter-arguments include legal citations
- [ ] Save/list/delete counter-arguments works
- [ ] History page shows all activity types (conversations, uploads, documents, counter-args)
- [ ] Search history by keyword works
- [ ] Resume a previous conversation works
- [ ] Delete history item works
- [ ] Dashboard recent activity shows last 5 items

### Deliverable
> **All 4 core AI features work. User can browse, search, and manage their history.**

### Dependencies & Blockers
- 🔗 Depends on: Sprint 2 (RAG pipeline), Sprint 3 (upload data), Sprint 4 (document data)

---

## Sprint 6: Profile, Polish & Launch Prep

**Goal:** MVP is demo-ready with landing page, theme support, error handling, and rate limiting.

### Frontend Tasks

| # | Task | Component/File | Priority |
|---|------|---------------|:--------:|
| F6.1 | Create ProfileForm component (edit name, role) | `src/components/profile/ProfileForm.jsx` | P0 |
| F6.2 | Create PreferencesForm component (theme toggle) | `src/components/profile/PreferencesForm.jsx` | P1 |
| F6.3 | Create ProfilePage (profile + preferences) | `src/pages/ProfilePage.jsx` | P0 |
| F6.4 | Create profileService (get, update profile) | `src/services/profileService.js` | P0 |
| F6.5 | Create ThemeContext (light/dark mode state) | `src/contexts/ThemeContext.jsx` | P1 |
| F6.6 | Implement dark mode CSS | `src/styles/index.css` | P1 |
| F6.7 | Create LandingPage (hero, features, CTA, testimonials) | `src/pages/LandingPage.jsx` | P0 |
| F6.8 | Create Modal component | `src/components/common/Modal.jsx` | P1 |
| F6.9 | Add loading states to all AI-powered features | All pages | P0 |
| F6.10 | Add error states and error toasts | All pages | P0 |
| F6.11 | Add empty states to all list pages | All pages | P1 |
| F6.12 | Add form validation to all forms | `src/utils/validators.js` | P1 |
| F6.13 | Handle rate limit errors (429) in Axios interceptor | `src/services/api.js` | P0 |
| F6.14 | Responsive design pass (mobile, tablet, desktop) | All components | P1 |

### Backend Tasks

| # | Task | File | Priority |
|---|------|------|:--------:|
| B6.1 | Create profile routes (GET, PUT) | `app/routes/profile_routes.py` | P0 |
| B6.2 | Create profile service | `app/services/profile_service.py` | P0 |
| B6.3 | Create profile schemas | `app/schemas/profile_schemas.py` | P0 |
| B6.4 | Implement rate limiting (slowapi) on all AI endpoints | `app/main.py`, routes | P0 |
| B6.5 | Add structured logging (API requests, AI calls, errors) | `app/middleware/` | P1 |
| B6.6 | Review and harden error responses (no stack traces in production) | `app/middleware/error_handler.py` | P0 |
| B6.7 | Expand legal corpus (add remaining acts and judgments) | `backend/corpus/` | P1 |
| B6.8 | Create .env.example with all required variables documented | `.env.example` | P0 |

### Testing

- [ ] Profile view/edit works
- [ ] Theme toggle works (light ↔ dark)
- [ ] Landing page renders with all sections
- [ ] Rate limiting returns 429 when exceeded
- [ ] All error states display user-friendly messages
- [ ] All loading states show spinners/skeleton screens
- [ ] End-to-end: signup → dashboard → use all features → logout
- [ ] Test with real legal questions (prepare 20 test queries)
- [ ] Cross-browser check (Chrome, Firefox, Edge)

### Deliverable
> **MVP is complete and demo-ready. Landing page looks professional. All features work with proper error handling.**

### Dependencies & Blockers
- 🔗 Depends on: Sprints 1-5 (all features complete)
- 📦 Required: slowapi library

---

## Summary

| Sprint | Duration | Key Deliverable |
|:------:|:--------:|----------------|
| 1 | Week 1 | Auth + empty dashboard |
| 2 | Week 2 | Know Your Kanoon (legal Q&A with RAG) |
| 3 | Week 3 | Upload & Chat (document analysis) |
| 4 | Week 4 | DocHub (document generation + export) |
| 5 | Week 5 | Counter Arguments + Chat History |
| 6 | Week 6 | Profile + Polish + Landing Page |

**Total: 6 weeks to demo-ready MVP.**
