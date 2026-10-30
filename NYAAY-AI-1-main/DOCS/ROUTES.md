# NYAAY AI — Routes Design

> **Version:** 1.0  
> **Date:** 2026-06-23  
> **Status:** Draft  
> **Frontend Router:** React Router v6  
> **Backend Framework:** FastAPI  
> **Document Type:** Technical Design Specification

---

## Table of Contents

1. [Overview](#1-overview)
2. [Frontend Routes](#2-frontend-routes)
   - 2.1 [Route Registry](#21-route-registry)
   - 2.2 [Public Routes](#22-public-routes)
   - 2.3 [Protected Routes](#23-protected-routes)
   - 2.4 [Layouts](#24-layouts)
   - 2.5 [Route Protection Logic](#25-route-protection-logic)
3. [Backend API Routes](#3-backend-api-routes)
   - 3.1 [API Conventions](#31-api-conventions)
   - 3.2 [Auth Routes — `/api/auth`](#32-auth-routes--apiauth)
   - 3.3 [Chat Routes — `/api/chat`](#33-chat-routes--apichat)
   - 3.4 [Upload Routes — `/api/upload`](#34-upload-routes--apiupload)
   - 3.5 [Document Routes — `/api/documents`](#35-document-routes--apidocuments)
   - 3.6 [Counter Argument Routes — `/api/counter`](#36-counter-argument-routes--apicounter)
   - 3.7 [Profile Routes — `/api/profile`](#37-profile-routes--apiprofile)
   - 3.8 [History Routes — `/api/history`](#38-history-routes--apihistory)
4. [Navigation Flows](#4-navigation-flows)
   - 4.1 [Authentication Flow](#41-authentication-flow)
   - 4.2 [Feature Navigation Flow](#42-feature-navigation-flow)
   - 4.3 [Redirect Rules](#43-redirect-rules)
5. [Error Handling](#5-error-handling)

---

## 1. Overview

This document defines the complete routing architecture for NYAAY AI across both the React frontend and FastAPI backend.

**Routing Architecture Summary:**

| Layer | Technology | Base URL |
|---|---|---|
| Frontend | React Router v6 (BrowserRouter) | `http://localhost:5173` (dev) |
| Backend | FastAPI with APIRouter | `http://localhost:8000/api` |

**Authentication Model:**
- Firebase Auth SDK handles login/signup on the frontend
- Firebase ID token is sent as `Authorization: Bearer <token>` header on every API request
- Backend verifies tokens using Firebase Admin SDK
- No session cookies; stateless JWT-based auth

---

## 2. Frontend Routes

### 2.1 Route Registry

| # | Path | Component | Auth | Layout | Description |
|---|---|---|---|---|---|
| 1 | `/` | `LandingPage` | No | `PublicLayout` | Marketing landing page |
| 2 | `/login` | `LoginPage` | No | `PublicLayout` | Email/password + Google login |
| 3 | `/signup` | `SignupPage` | No | `PublicLayout` | Registration with role selection |
| 4 | `/dashboard` | `DashboardPage` | Yes | `DashboardLayout` | Feature hub with quick actions |
| 5 | `/know-your-kanoon` | `KnowKanoonPage` | Yes | `DashboardLayout` | Legal Q&A chat with RAG |
| 6 | `/upload-chat` | `UploadChatPage` | Yes | `DashboardLayout` | Upload documents and chat |
| 7 | `/dochub` | `DocHubPage` | Yes | `DashboardLayout` | Template selection (3 templates) |
| 8 | `/dochub/:templateId` | `DocHubGeneratePage` | Yes | `DashboardLayout` | Generate document from template |
| 9 | `/counter-arguments` | `CounterArgumentPage` | Yes | `DashboardLayout` | Counter-argument generator |
| 10 | `/profile` | `ProfilePage` | Yes | `DashboardLayout` | User profile & preferences |
| 11 | `/history` | `ChatHistoryPage` | Yes | `DashboardLayout` | All chat history listing |
| 12 | `/history/:chatId` | `ChatDetailPage` | Yes | `DashboardLayout` | View specific conversation |

### 2.2 Public Routes

These routes are accessible without authentication. Authenticated users accessing these routes are redirected to `/dashboard`.

---

#### `GET /`  — Landing Page

| Property | Value |
|---|---|
| **Component** | `LandingPage` |
| **Layout** | `PublicLayout` |
| **Auth Required** | No |
| **Redirect if Authed** | → `/dashboard` |
| **Description** | Marketing page showcasing NYAAY AI features, target audience (Citizens, Students, Lawyers), call-to-action for signup/login |

**Page Sections:**
- Hero section with tagline
- Feature highlights (Know Your Kanoon, Upload & Chat, DocHub, Counter Arguments)
- Role-based benefits (Citizen / Student / Lawyer)
- CTA buttons → `/signup`, `/login`

---

#### `GET /login` — Login Page

| Property | Value |
|---|---|
| **Component** | `LoginPage` |
| **Layout** | `PublicLayout` |
| **Auth Required** | No |
| **Redirect if Authed** | → `/dashboard` |
| **Description** | Firebase email/password login + Google OAuth |

**Form Fields:**
- Email (text input, required)
- Password (password input, required)
- "Forgot Password?" link (triggers Firebase password reset)
- "Sign in with Google" button
- Link to `/signup` for new users

---

#### `GET /signup` — Signup Page

| Property | Value |
|---|---|
| **Component** | `SignupPage` |
| **Layout** | `PublicLayout` |
| **Auth Required** | No |
| **Redirect if Authed** | → `/dashboard` |
| **Description** | New user registration with role selection |

**Form Fields:**
- Full Name (text input, required)
- Email (text input, required)
- Password (password input, required, min 8 chars)
- Confirm Password (password input, required)
- Role (radio group: Citizen / Student / Lawyer, required)
- "Sign up with Google" button (role selection dialog after OAuth)
- Link to `/login` for existing users

---

### 2.3 Protected Routes

All protected routes require authentication. Unauthenticated users are redirected to `/login` with the intended path stored for post-login redirect.

---

#### `GET /dashboard` — Dashboard

| Property | Value |
|---|---|
| **Component** | `DashboardPage` |
| **Layout** | `DashboardLayout` |
| **Auth Required** | Yes |
| **Description** | Central hub showing feature cards, recent activity, and quick actions |

**Page Elements:**
- Welcome banner with user name and role
- Feature cards grid (4 features): Know Your Kanoon, Upload & Chat, DocHub, Counter Arguments
- Recent conversations sidebar (last 5 across all features)
- Quick stats: total conversations, documents generated, uploads

---

#### `GET /know-your-kanoon` — Legal Q&A

| Property | Value |
|---|---|
| **Component** | `KnowKanoonPage` |
| **Layout** | `DashboardLayout` |
| **Auth Required** | Yes |
| **Description** | RAG-powered legal Q&A chat interface |

**Page Elements:**
- Chat interface with message history
- Conversation sidebar (previous Know Your Kanoon conversations)
- New conversation button
- Message input with send button
- Citation display panel (collapsible, shows legal sources)

---

#### `GET /upload-chat` — Upload & Chat

| Property | Value |
|---|---|
| **Component** | `UploadChatPage` |
| **Layout** | `DashboardLayout` |
| **Auth Required** | Yes |
| **Description** | Upload documents (PDF/DOCX/TXT) and chat with their contents |

**Page Elements:**
- File upload zone (drag-and-drop + file picker)
- Upload constraints display: 10MB max, 300 pages max, PDF/DOCX/TXT
- Upload progress indicator with status (processing → ready → error)
- Chat interface (enabled after upload is `ready`)
- Previous uploads sidebar

---

#### `GET /dochub` — Document Hub

| Property | Value |
|---|---|
| **Component** | `DocHubPage` |
| **Layout** | `DashboardLayout` |
| **Auth Required** | Yes |
| **Description** | Template selection page with 3 document templates |

**Template Cards:**
| Template ID | Display Name | Route |
|---|---|---|
| `legal_notice` | Legal Notice | `/dochub/legal_notice` |
| `rental_agreement` | Rental Agreement | `/dochub/rental_agreement` |
| `affidavit` | Affidavit | `/dochub/affidavit` |

**Page Elements:**
- Template cards (3 cards with description and icon)
- Recent generated documents list
- Click on template card → navigates to `/dochub/:templateId`

---

#### `GET /dochub/:templateId` — Generate Document

| Property | Value |
|---|---|
| **Component** | `DocHubGeneratePage` |
| **Layout** | `DashboardLayout` |
| **Auth Required** | Yes |
| **URL Params** | `templateId`: one of `legal_notice`, `rental_agreement`, `affidavit` |
| **Description** | Dynamic form for generating a document from the selected template |

**Validation:**
- If `templateId` is not one of the 3 valid values → redirect to `/dochub` with error toast

**Page Elements:**
- Dynamic form (fields vary by template type)
- Preview panel (live preview of generated document)
- "Generate" button → calls API → displays result
- "Export as PDF" / "Export as DOCX" buttons
- "Save" button

---

#### `GET /counter-arguments` — Counter Argument Generator

| Property | Value |
|---|---|
| **Component** | `CounterArgumentPage` |
| **Layout** | `DashboardLayout` |
| **Auth Required** | Yes |
| **Description** | Input a legal argument and generate counter-arguments across 4 categories |

**Page Elements:**
- Argument input (textarea, required)
- "Generate Counter-Arguments" button
- Results display with 4 tabbed sections:
  - Opposing Viewpoints
  - Legal Rebuttals
  - Alternative Interpretations
  - Strategic Perspectives
- Save results button
- History sidebar (previous generations)

---

#### `GET /profile` — User Profile

| Property | Value |
|---|---|
| **Component** | `ProfilePage` |
| **Layout** | `DashboardLayout` |
| **Auth Required** | Yes |
| **Description** | View and edit user profile and preferences |

**Page Elements:**
- Display name (editable)
- Email (read-only, from Firebase)
- Role badge (read-only after signup)
- Preferences (theme, language)
- Account stats (member since, total conversations, total documents)
- Logout button

---

#### `GET /history` — Chat History

| Property | Value |
|---|---|
| **Component** | `ChatHistoryPage` |
| **Layout** | `DashboardLayout` |
| **Auth Required** | Yes |
| **Description** | Unified view of all conversations across all features |

**Page Elements:**
- Search bar (searches conversation titles)
- Feature filter tabs: All / Know Your Kanoon / Upload & Chat / Counter Arguments
- Conversation list with: title, feature type badge, date, message count
- Click on conversation → navigates to `/history/:chatId`
- Delete conversation button (with confirmation)

---

#### `GET /history/:chatId` — Chat Detail

| Property | Value |
|---|---|
| **Component** | `ChatDetailPage` |
| **Layout** | `DashboardLayout` |
| **Auth Required** | Yes |
| **URL Params** | `chatId`: conversation UUID |
| **Description** | Read-only view of a specific past conversation |

**Page Elements:**
- Conversation metadata (title, feature type, date range)
- Full message history (read-only)
- Citations panel
- "Continue Conversation" button → navigates to the feature page with this conversation loaded
- "Delete Conversation" button

---

### 2.4 Layouts

#### `PublicLayout`

| Property | Value |
|---|---|
| **Used By** | `/`, `/login`, `/signup` |
| **Components** | Navbar (logo, Login/Signup buttons), Footer |
| **Behavior** | No sidebar, full-width content area |

#### `DashboardLayout`

| Property | Value |
|---|---|
| **Used By** | All protected routes |
| **Components** | Top navbar (logo, user avatar, notifications), Sidebar (navigation links), Main content area |
| **Behavior** | Sidebar with links to all features, collapsible on mobile |

**Sidebar Navigation Items:**
```
📊  Dashboard          → /dashboard
⚖️  Know Your Kanoon   → /know-your-kanoon
📄  Upload & Chat      → /upload-chat
📝  DocHub             → /dochub
🔄  Counter Arguments  → /counter-arguments
📜  Chat History       → /history
👤  Profile            → /profile
🚪  Logout             → (triggers Firebase signOut)
```

---

### 2.5 Route Protection Logic

```
┌──────────────────────────────┐
│     User navigates to URL     │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│   Is route public or         │
│   protected?                 │
└──────┬───────────┬───────────┘
       │           │
   Public      Protected
       │           │
       ▼           ▼
┌────────────┐ ┌──────────────────┐
│ Is user    │ │ Is user          │
│ authed?    │ │ authenticated?   │
└──┬─────┬──┘ └──┬───────────┬──┘
   │     │       │           │
  Yes    No     Yes          No
   │     │       │           │
   ▼     ▼       ▼           ▼
┌──────┐ ┌───┐ ┌──────┐ ┌──────────────────┐
│Redir │ │Ren│ │Render│ │ Redirect to      │
│to    │ │der│ │ page │ │ /login?redirect=  │
│/dash │ │pg │ │      │ │ {intended_path}   │
└──────┘ └───┘ └──────┘ └──────────────────┘
```

**Implementation Pattern (React Router v6):**

```
ProtectedRoute wrapper component:
1. Check Firebase auth state (useAuthState hook)
2. If loading → show spinner
3. If not authenticated → Navigate to /login?redirect={current_path}
4. If authenticated → render <Outlet />

PublicRoute wrapper component:
1. Check Firebase auth state
2. If loading → show spinner
3. If authenticated → Navigate to /dashboard
4. If not authenticated → render <Outlet />
```

---

## 3. Backend API Routes

### 3.1 API Conventions

| Convention | Value |
|---|---|
| **Base URL** | `/api` |
| **Content Type** | `application/json` (except file uploads: `multipart/form-data`) |
| **Auth Header** | `Authorization: Bearer <firebase_id_token>` |
| **Date Format** | ISO 8601 UTC: `YYYY-MM-DDTHH:MM:SSZ` |
| **ID Format** | UUID v4 strings |
| **Pagination** | Query params: `?page=1&limit=20` (default limit: 20, max: 100) |
| **Error Format** | `{ "detail": "Error message", "code": "ERROR_CODE" }` |

**Standard Response Envelope:**

```json
{
  "success": true,
  "data": { ... },
  "message": "Optional human-readable message"
}
```

**Paginated Response Envelope:**

```json
{
  "success": true,
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 42,
    "total_pages": 3
  }
}
```

**Standard HTTP Status Codes:**

| Code | Usage |
|---|---|
| `200` | Success (GET, PUT, DELETE) |
| `201` | Created (POST) |
| `400` | Bad request / validation error |
| `401` | Unauthorized (missing or invalid token) |
| `403` | Forbidden (valid token but no access) |
| `404` | Resource not found |
| `413` | Payload too large (file upload exceeds 10MB) |
| `422` | Unprocessable entity (semantic validation failure) |
| `500` | Internal server error |

---

### 3.2 Auth Routes — `/api/auth`

---

#### `POST /api/auth/register`

| Property | Value |
|---|---|
| **Auth** | Required (Firebase token from just-created account) |
| **Description** | Register a new user in the local database after Firebase account creation |

**Request Body:**
```json
{
  "name": "Ansh Darji",
  "role": "student"
}
```

| Field | Type | Required | Validation |
|---|---|---|---|
| `name` | string | Yes | 1–100 characters |
| `role` | string | Yes | One of: `citizen`, `student`, `lawyer` |

**Response (201):**
```json
{
  "success": true,
  "data": {
    "firebase_uid": "abc123xyz",
    "email": "ansh@example.com",
    "name": "Ansh Darji",
    "role": "student",
    "preferences": {},
    "created_at": "2026-06-23T00:00:00Z"
  },
  "message": "User registered successfully"
}
```

**Errors:**
| Code | Condition |
|---|---|
| `400` | Invalid role value |
| `401` | Invalid/missing Firebase token |
| `409` | User already exists in local DB |

---

#### `POST /api/auth/login`

| Property | Value |
|---|---|
| **Auth** | Required (Firebase token) |
| **Description** | Record a login event and return user profile; updates `last_login` timestamp |

**Request Body:** None (user identified from Firebase token)

**Response (200):**
```json
{
  "success": true,
  "data": {
    "firebase_uid": "abc123xyz",
    "email": "ansh@example.com",
    "name": "Ansh Darji",
    "role": "student",
    "preferences": { "theme": "dark" },
    "created_at": "2026-06-23T00:00:00Z",
    "last_login": "2026-06-23T12:00:00Z"
  }
}
```

**Errors:**
| Code | Condition |
|---|---|
| `401` | Invalid/missing Firebase token |
| `404` | Firebase user not found in local DB (should call `/register` first) |

---

#### `GET /api/auth/me`

| Property | Value |
|---|---|
| **Auth** | Required |
| **Description** | Get current authenticated user's profile |

**Request Body:** None

**Response (200):**
```json
{
  "success": true,
  "data": {
    "firebase_uid": "abc123xyz",
    "email": "ansh@example.com",
    "name": "Ansh Darji",
    "role": "student",
    "preferences": { "theme": "dark", "language": "en" },
    "created_at": "2026-06-23T00:00:00Z",
    "last_login": "2026-06-23T12:00:00Z"
  }
}
```

---

### 3.3 Chat Routes — `/api/chat`

---

#### `POST /api/chat/send`

| Property | Value |
|---|---|
| **Auth** | Required |
| **Description** | Send a message in a conversation and receive the AI response. Creates a new conversation if `conversation_id` is not provided. |

**Request Body:**
```json
{
  "conversation_id": "uuid-string-or-null",
  "message": "What is Article 21 of the Indian Constitution?",
  "feature_type": "know_kanoon"
}
```

| Field | Type | Required | Validation |
|---|---|---|---|
| `conversation_id` | string \| null | No | Valid UUID if provided; null to create new conversation |
| `message` | string | Yes | 1–5000 characters |
| `feature_type` | string | Yes (if new) | One of: `know_kanoon`, `upload_chat`, `counter_arg` |

**Response (200):**
```json
{
  "success": true,
  "data": {
    "conversation_id": "conv-uuid-123",
    "user_message": {
      "id": 1,
      "role": "user",
      "content": "What is Article 21 of the Indian Constitution?",
      "created_at": "2026-06-23T12:00:00Z"
    },
    "assistant_message": {
      "id": 2,
      "role": "assistant",
      "content": "Article 21 of the Indian Constitution guarantees the Right to Life and Personal Liberty...",
      "citations": [
        {
          "source": "Constitution of India",
          "section": "Article 21",
          "text": "No person shall be deprived of his life or personal liberty except according to procedure established by law.",
          "relevance_score": 0.95
        }
      ],
      "created_at": "2026-06-23T12:00:01Z"
    }
  }
}
```

---

#### `GET /api/chat/conversations`

| Property | Value |
|---|---|
| **Auth** | Required |
| **Description** | List all conversations for the current user, optionally filtered by feature type |

**Query Parameters:**

| Param | Type | Required | Default | Description |
|---|---|---|---|---|
| `feature_type` | string | No | — | Filter by: `know_kanoon`, `upload_chat`, `counter_arg` |
| `page` | integer | No | `1` | Page number |
| `limit` | integer | No | `20` | Items per page (max 100) |

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "conv-uuid-123",
      "title": "Article 21 Discussion",
      "feature_type": "know_kanoon",
      "message_count": 6,
      "created_at": "2026-06-23T10:00:00Z",
      "updated_at": "2026-06-23T12:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 5,
    "total_pages": 1
  }
}
```

---

#### `GET /api/chat/conversations/{conversation_id}`

| Property | Value |
|---|---|
| **Auth** | Required |
| **Description** | Get a specific conversation with all its messages |

**Path Parameters:**

| Param | Type | Description |
|---|---|---|
| `conversation_id` | string (UUID) | Conversation ID |

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "conv-uuid-123",
    "title": "Article 21 Discussion",
    "feature_type": "know_kanoon",
    "created_at": "2026-06-23T10:00:00Z",
    "updated_at": "2026-06-23T12:00:00Z",
    "messages": [
      {
        "id": 1,
        "role": "user",
        "content": "What is Article 21?",
        "citations": null,
        "created_at": "2026-06-23T10:00:00Z"
      },
      {
        "id": 2,
        "role": "assistant",
        "content": "Article 21 guarantees...",
        "citations": [ { "source": "Constitution of India", "section": "Article 21", "text": "...", "relevance_score": 0.95 } ],
        "created_at": "2026-06-23T10:00:01Z"
      }
    ]
  }
}
```

**Errors:**
| Code | Condition |
|---|---|
| `404` | Conversation not found or doesn't belong to user |

---

#### `DELETE /api/chat/conversations/{conversation_id}`

| Property | Value |
|---|---|
| **Auth** | Required |
| **Description** | Soft-delete a conversation (sets `is_active = 0`) |

**Path Parameters:**

| Param | Type | Description |
|---|---|---|
| `conversation_id` | string (UUID) | Conversation ID |

**Response (200):**
```json
{
  "success": true,
  "message": "Conversation deleted successfully"
}
```

---

### 3.4 Upload Routes — `/api/upload`

---

#### `POST /api/upload/file`

| Property | Value |
|---|---|
| **Auth** | Required |
| **Content-Type** | `multipart/form-data` |
| **Description** | Upload a document file for processing and embedding into ChromaDB |

**Request (multipart/form-data):**

| Field | Type | Required | Validation |
|---|---|---|---|
| `file` | file | Yes | PDF/DOCX/TXT, max 10MB, max 300 pages |

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "upload-uuid-456",
    "original_name": "contract.pdf",
    "file_type": "pdf",
    "file_size": 2048576,
    "page_count": 45,
    "status": "processing",
    "created_at": "2026-06-23T12:00:00Z"
  },
  "message": "File uploaded successfully. Processing in progress."
}
```

**Errors:**
| Code | Condition |
|---|---|
| `400` | Invalid file type (not PDF/DOCX/TXT) |
| `413` | File exceeds 10MB |
| `422` | Document exceeds 300 pages |

---

#### `POST /api/upload/{upload_id}/chat`

| Property | Value |
|---|---|
| **Auth** | Required |
| **Description** | Chat with an uploaded document. Creates or continues a conversation linked to this upload. |

**Path Parameters:**

| Param | Type | Description |
|---|---|---|
| `upload_id` | string (UUID) | Upload ID |

**Request Body:**
```json
{
  "conversation_id": "conv-uuid-or-null",
  "message": "Summarize the key clauses in this contract"
}
```

| Field | Type | Required | Validation |
|---|---|---|---|
| `conversation_id` | string \| null | No | Valid UUID if provided; null to create new |
| `message` | string | Yes | 1–5000 characters |

**Response (200):**
```json
{
  "success": true,
  "data": {
    "conversation_id": "conv-uuid-789",
    "user_message": {
      "id": 1,
      "role": "user",
      "content": "Summarize the key clauses in this contract",
      "created_at": "2026-06-23T12:05:00Z"
    },
    "assistant_message": {
      "id": 2,
      "role": "assistant",
      "content": "The contract contains the following key clauses...",
      "citations": [
        {
          "source": "contract.pdf",
          "section": "Clause 3.1",
          "text": "The tenant shall pay a monthly rent of...",
          "relevance_score": 0.89
        }
      ],
      "created_at": "2026-06-23T12:05:02Z"
    }
  }
}
```

**Errors:**
| Code | Condition |
|---|---|
| `404` | Upload not found or doesn't belong to user |
| `409` | Upload status is not `ready` (still processing or errored) |

---

#### `GET /api/upload/list`

| Property | Value |
|---|---|
| **Auth** | Required |
| **Description** | List all uploads for the current user |

**Query Parameters:**

| Param | Type | Required | Default | Description |
|---|---|---|---|---|
| `status` | string | No | — | Filter by: `processing`, `ready`, `error` |
| `page` | integer | No | `1` | Page number |
| `limit` | integer | No | `20` | Items per page |

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "upload-uuid-456",
      "original_name": "contract.pdf",
      "file_type": "pdf",
      "file_size": 2048576,
      "page_count": 45,
      "status": "ready",
      "conversation_id": "conv-uuid-789",
      "created_at": "2026-06-23T12:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 3,
    "total_pages": 1
  }
}
```

---

#### `DELETE /api/upload/{upload_id}`

| Property | Value |
|---|---|
| **Auth** | Required |
| **Description** | Delete an upload and its associated ChromaDB collection |

**Path Parameters:**

| Param | Type | Description |
|---|---|---|
| `upload_id` | string (UUID) | Upload ID |

**Response (200):**
```json
{
  "success": true,
  "message": "Upload and associated data deleted successfully"
}
```

**Side Effects:**
- Deletes the file from disk
- Deletes the ChromaDB collection (embeddings)
- Does NOT delete the linked conversation (preserved for history)

---

### 3.5 Document Routes — `/api/documents`

---

#### `GET /api/documents/templates`

| Property | Value |
|---|---|
| **Auth** | Required |
| **Description** | Get the list of available document templates with their field schemas |

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "legal_notice",
      "name": "Legal Notice",
      "description": "Draft a formal legal notice under Indian law",
      "fields": [
        { "name": "sender_name", "type": "text", "label": "Sender Name", "required": true },
        { "name": "sender_address", "type": "textarea", "label": "Sender Address", "required": true },
        { "name": "recipient_name", "type": "text", "label": "Recipient Name", "required": true },
        { "name": "recipient_address", "type": "textarea", "label": "Recipient Address", "required": true },
        { "name": "subject", "type": "text", "label": "Subject of Notice", "required": true },
        { "name": "facts", "type": "textarea", "label": "Statement of Facts", "required": true },
        { "name": "legal_grounds", "type": "textarea", "label": "Legal Grounds", "required": false },
        { "name": "relief_sought", "type": "textarea", "label": "Relief Sought", "required": true },
        { "name": "response_deadline_days", "type": "number", "label": "Response Deadline (days)", "required": true }
      ]
    },
    {
      "id": "rental_agreement",
      "name": "Rental Agreement",
      "description": "Generate a rental/lease agreement compliant with Indian tenancy laws",
      "fields": [
        { "name": "landlord_name", "type": "text", "label": "Landlord Name", "required": true },
        { "name": "tenant_name", "type": "text", "label": "Tenant Name", "required": true },
        { "name": "property_address", "type": "textarea", "label": "Property Address", "required": true },
        { "name": "monthly_rent", "type": "number", "label": "Monthly Rent (₹)", "required": true },
        { "name": "security_deposit", "type": "number", "label": "Security Deposit (₹)", "required": true },
        { "name": "lease_start_date", "type": "date", "label": "Lease Start Date", "required": true },
        { "name": "lease_duration_months", "type": "number", "label": "Lease Duration (months)", "required": true },
        { "name": "special_terms", "type": "textarea", "label": "Special Terms & Conditions", "required": false }
      ]
    },
    {
      "id": "affidavit",
      "name": "Affidavit",
      "description": "Create a sworn affidavit for use in Indian courts",
      "fields": [
        { "name": "deponent_name", "type": "text", "label": "Deponent Name", "required": true },
        { "name": "father_name", "type": "text", "label": "Father's/Husband's Name", "required": true },
        { "name": "age", "type": "number", "label": "Age", "required": true },
        { "name": "address", "type": "textarea", "label": "Residential Address", "required": true },
        { "name": "purpose", "type": "text", "label": "Purpose of Affidavit", "required": true },
        { "name": "statements", "type": "textarea", "label": "Statements of Fact (one per line)", "required": true },
        { "name": "court_name", "type": "text", "label": "Court/Authority Name", "required": false },
        { "name": "verification_place", "type": "text", "label": "Place of Verification", "required": true }
      ]
    }
  ]
}
```

---

#### `POST /api/documents/generate`

| Property | Value |
|---|---|
| **Auth** | Required |
| **Description** | Generate a document from a template using AI |

**Request Body:**
```json
{
  "template_type": "legal_notice",
  "title": "Notice to Landlord — Maintenance Issues",
  "fields": {
    "sender_name": "Ansh Darji",
    "sender_address": "123, MG Road, Ahmedabad, Gujarat",
    "recipient_name": "Property Owner",
    "recipient_address": "456, SG Highway, Ahmedabad, Gujarat",
    "subject": "Failure to maintain premises",
    "facts": "The landlord has failed to repair the plumbing for 3 months...",
    "legal_grounds": "Section 14 of the Gujarat Rent Control Act",
    "relief_sought": "Immediate repairs within 15 days",
    "response_deadline_days": 15
  }
}
```

| Field | Type | Required | Validation |
|---|---|---|---|
| `template_type` | string | Yes | One of: `legal_notice`, `rental_agreement`, `affidavit` |
| `title` | string | Yes | 1–200 characters |
| `fields` | object | Yes | Must match the template's field schema |

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "doc-uuid-101",
    "title": "Notice to Landlord — Maintenance Issues",
    "template_type": "legal_notice",
    "content": "# LEGAL NOTICE\n\nTo,\nProperty Owner\n456, SG Highway...\n\nSub: Failure to maintain premises...",
    "doc_type": "generated",
    "created_at": "2026-06-23T14:00:00Z"
  },
  "message": "Document generated successfully"
}
```

---

#### `POST /api/documents/{document_id}/export`

| Property | Value |
|---|---|
| **Auth** | Required |
| **Description** | Export a generated document as PDF or DOCX |

**Path Parameters:**

| Param | Type | Description |
|---|---|---|
| `document_id` | string (UUID) | Document ID |

**Request Body:**
```json
{
  "format": "pdf"
}
```

| Field | Type | Required | Validation |
|---|---|---|---|
| `format` | string | Yes | One of: `pdf`, `docx` |

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "doc-uuid-101",
    "doc_type": "exported",
    "file_path": "/exports/doc-uuid-101.pdf",
    "download_url": "/api/documents/doc-uuid-101/download"
  },
  "message": "Document exported successfully"
}
```

---

#### `GET /api/documents/list`

| Property | Value |
|---|---|
| **Auth** | Required |
| **Description** | List all saved documents for the current user |

**Query Parameters:**

| Param | Type | Required | Default | Description |
|---|---|---|---|---|
| `template_type` | string | No | — | Filter by template type |
| `page` | integer | No | `1` | Page number |
| `limit` | integer | No | `20` | Items per page |

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "doc-uuid-101",
      "title": "Notice to Landlord — Maintenance Issues",
      "template_type": "legal_notice",
      "doc_type": "exported",
      "created_at": "2026-06-23T14:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 2,
    "total_pages": 1
  }
}
```

---

#### `GET /api/documents/{document_id}`

| Property | Value |
|---|---|
| **Auth** | Required |
| **Description** | Get a specific document with full content |

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "doc-uuid-101",
    "title": "Notice to Landlord — Maintenance Issues",
    "template_type": "legal_notice",
    "content": "# LEGAL NOTICE\n\n...",
    "doc_type": "exported",
    "file_path": "/exports/doc-uuid-101.pdf",
    "created_at": "2026-06-23T14:00:00Z"
  }
}
```

---

#### `DELETE /api/documents/{document_id}`

| Property | Value |
|---|---|
| **Auth** | Required |
| **Description** | Delete a saved document and its exported file |

**Response (200):**
```json
{
  "success": true,
  "message": "Document deleted successfully"
}
```

---

### 3.6 Counter Argument Routes — `/api/counter`

---

#### `POST /api/counter/generate`

| Property | Value |
|---|---|
| **Auth** | Required |
| **Description** | Generate counter-arguments for a given legal argument across 4 categories |

**Request Body:**
```json
{
  "argument": "The tenant has no right to withhold rent even if the landlord fails to maintain the property."
}
```

| Field | Type | Required | Validation |
|---|---|---|---|
| `argument` | string | Yes | 10–5000 characters |

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "ca-uuid-201",
    "input_argument": "The tenant has no right to withhold rent...",
    "result": {
      "opposing_viewpoints": [
        {
          "title": "Tenant's Right to Habitable Premises",
          "argument": "Under common law and various state rent control acts...",
          "legal_basis": "Section 14, Gujarat Rent Control Act",
          "strength": "strong"
        }
      ],
      "legal_rebuttals": [
        {
          "title": "Implied Warranty of Habitability",
          "argument": "Indian courts have recognized...",
          "legal_basis": "Transfer of Property Act, Section 108(e)",
          "strength": "strong"
        }
      ],
      "alternative_interpretations": [
        {
          "title": "Partial Withholding Approach",
          "argument": "Rather than complete withholding...",
          "legal_basis": "Judicial precedent in Smt. X vs. Y",
          "strength": "moderate"
        }
      ],
      "strategic_perspectives": [
        {
          "title": "Negotiate Before Withholding",
          "argument": "A strategic approach would be to...",
          "legal_basis": "Section 89, CPC (Mediation)",
          "strength": "moderate"
        }
      ]
    },
    "created_at": "2026-06-23T15:00:00Z"
  }
}
```

---

#### `GET /api/counter/list`

| Property | Value |
|---|---|
| **Auth** | Required |
| **Description** | List all saved counter-argument generations for the current user |

**Query Parameters:**

| Param | Type | Required | Default | Description |
|---|---|---|---|---|
| `page` | integer | No | `1` | Page number |
| `limit` | integer | No | `20` | Items per page |

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "ca-uuid-201",
      "input_argument": "The tenant has no right to withhold rent...",
      "created_at": "2026-06-23T15:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 1,
    "total_pages": 1
  }
}
```

---

#### `GET /api/counter/{counter_id}`

| Property | Value |
|---|---|
| **Auth** | Required |
| **Description** | Get a specific counter-argument generation with full results |

**Path Parameters:**

| Param | Type | Description |
|---|---|---|
| `counter_id` | string (UUID) | Counter-argument ID |

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "ca-uuid-201",
    "input_argument": "The tenant has no right to withhold rent...",
    "result": {
      "opposing_viewpoints": [ ... ],
      "legal_rebuttals": [ ... ],
      "alternative_interpretations": [ ... ],
      "strategic_perspectives": [ ... ]
    },
    "created_at": "2026-06-23T15:00:00Z"
  }
}
```

---

#### `DELETE /api/counter/{counter_id}`

| Property | Value |
|---|---|
| **Auth** | Required |
| **Description** | Delete a saved counter-argument generation |

**Response (200):**
```json
{
  "success": true,
  "message": "Counter-argument deleted successfully"
}
```

---

### 3.7 Profile Routes — `/api/profile`

---

#### `GET /api/profile`

| Property | Value |
|---|---|
| **Auth** | Required |
| **Description** | Get the current user's full profile with stats |

**Response (200):**
```json
{
  "success": true,
  "data": {
    "firebase_uid": "abc123xyz",
    "email": "ansh@example.com",
    "name": "Ansh Darji",
    "role": "student",
    "preferences": {
      "theme": "dark",
      "language": "en"
    },
    "stats": {
      "total_conversations": 12,
      "total_documents": 3,
      "total_uploads": 5,
      "total_counter_arguments": 2
    },
    "created_at": "2026-06-23T00:00:00Z",
    "last_login": "2026-06-23T12:00:00Z"
  }
}
```

---

#### `PUT /api/profile`

| Property | Value |
|---|---|
| **Auth** | Required |
| **Description** | Update the current user's profile (name and preferences only) |

**Request Body:**
```json
{
  "name": "Ansh D.",
  "preferences": {
    "theme": "dark",
    "language": "hi",
    "notifications": false
  }
}
```

| Field | Type | Required | Validation |
|---|---|---|---|
| `name` | string | No | 1–100 characters |
| `preferences` | object | No | Valid JSON object |

**Response (200):**
```json
{
  "success": true,
  "data": {
    "firebase_uid": "abc123xyz",
    "email": "ansh@example.com",
    "name": "Ansh D.",
    "role": "student",
    "preferences": {
      "theme": "dark",
      "language": "hi",
      "notifications": false
    },
    "created_at": "2026-06-23T00:00:00Z",
    "last_login": "2026-06-23T12:00:00Z"
  },
  "message": "Profile updated successfully"
}
```

> **Note:** `email` and `role` are read-only after registration. Email changes must go through Firebase Auth directly.

---

### 3.8 History Routes — `/api/history`

---

#### `GET /api/history`

| Property | Value |
|---|---|
| **Auth** | Required |
| **Description** | Get unified chat history across all features for the current user |

**Query Parameters:**

| Param | Type | Required | Default | Description |
|---|---|---|---|---|
| `feature_type` | string | No | — | Filter by: `know_kanoon`, `upload_chat`, `counter_arg` |
| `page` | integer | No | `1` | Page number |
| `limit` | integer | No | `20` | Items per page |
| `sort` | string | No | `desc` | Sort order: `asc` or `desc` (by `updated_at`) |

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "conv-uuid-123",
      "title": "Article 21 Discussion",
      "feature_type": "know_kanoon",
      "message_count": 6,
      "first_message_preview": "What is Article 21 of the...",
      "created_at": "2026-06-23T10:00:00Z",
      "updated_at": "2026-06-23T12:00:00Z"
    },
    {
      "id": "conv-uuid-789",
      "title": "Contract Analysis",
      "feature_type": "upload_chat",
      "message_count": 4,
      "first_message_preview": "Summarize the key clauses...",
      "created_at": "2026-06-23T12:00:00Z",
      "updated_at": "2026-06-23T12:05:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 15,
    "total_pages": 1
  }
}
```

---

#### `GET /api/history/search`

| Property | Value |
|---|---|
| **Auth** | Required |
| **Description** | Search conversation history by title or message content |

**Query Parameters:**

| Param | Type | Required | Default | Description |
|---|---|---|---|---|
| `q` | string | Yes | — | Search query (min 2 characters) |
| `feature_type` | string | No | — | Filter by feature type |
| `page` | integer | No | `1` | Page number |
| `limit` | integer | No | `20` | Items per page |

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "conv-uuid-123",
      "title": "Article 21 Discussion",
      "feature_type": "know_kanoon",
      "match_context": "...Article 21 of the Indian Constitution guarantees...",
      "created_at": "2026-06-23T10:00:00Z",
      "updated_at": "2026-06-23T12:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 1,
    "total_pages": 1
  }
}
```

---

#### `DELETE /api/history/{conversation_id}`

| Property | Value |
|---|---|
| **Auth** | Required |
| **Description** | Delete a specific conversation from history (soft delete) |

**Path Parameters:**

| Param | Type | Description |
|---|---|---|
| `conversation_id` | string (UUID) | Conversation ID |

**Response (200):**
```json
{
  "success": true,
  "message": "History item deleted successfully"
}
```

---

## 4. Navigation Flows

### 4.1 Authentication Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────────────────────┐
│              │     │              │     │                              │
│  Landing     │────▶│  /login      │────▶│  Firebase Auth               │
│  Page (/)    │     │  or /signup  │     │  (email/password or Google)  │
│              │     │              │     │                              │
└──────────────┘     └──────────────┘     └──────────────┬───────────────┘
                                                         │
                                                         │ On Success
                                                         ▼
                                          ┌──────────────────────────────┐
                                          │  Frontend receives           │
                                          │  Firebase ID Token           │
                                          └──────────────┬───────────────┘
                                                         │
                                          ┌──────────────┴───────────────┐
                                          │                              │
                                     New User?                    Existing User?
                                          │                              │
                                          ▼                              ▼
                                  POST /api/auth/register      POST /api/auth/login
                                          │                              │
                                          └──────────────┬───────────────┘
                                                         │
                                                         ▼
                                          ┌──────────────────────────────┐
                                          │  Store user data in          │
                                          │  React context / local state │
                                          └──────────────┬───────────────┘
                                                         │
                                                         ▼
                                          ┌──────────────────────────────┐
                                          │  Redirect to:                │
                                          │  ?redirect param || /dashboard│
                                          └──────────────────────────────┘
```

**Token Lifecycle:**
1. Firebase SDK manages token refresh automatically
2. Frontend attaches `Authorization: Bearer <token>` to every API call via Axios interceptor
3. Backend verifies token on every request via Firebase Admin SDK middleware
4. On token expiry/invalid → API returns `401` → Frontend redirects to `/login`

---

### 4.2 Feature Navigation Flow

```
┌────────────────────────────────────────────────────────────────┐
│                         /dashboard                              │
│                                                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  ┌────────┐ │
│  │ Know Your    │  │ Upload &     │  │  DocHub  │  │Counter │ │
│  │ Kanoon       │  │ Chat         │  │          │  │Args    │ │
│  └──────┬───────┘  └──────┬───────┘  └────┬─────┘  └───┬────┘ │
│         │                 │               │             │      │
└─────────┼─────────────────┼───────────────┼─────────────┼──────┘
          │                 │               │             │
          ▼                 ▼               ▼             ▼
  /know-your-kanoon   /upload-chat      /dochub     /counter-arguments
          │                 │               │             │
          │                 │               ▼             │
          │                 │        /dochub/:templateId  │
          │                 │               │             │
          ▼                 ▼               ▼             ▼
    ┌──────────────────────────────────────────────────────────┐
    │                     /history                              │
    │              (all conversations)                          │
    │                        │                                  │
    │                        ▼                                  │
    │               /history/:chatId                            │
    │          (view specific conversation)                     │
    │                        │                                  │
    │                        ▼                                  │
    │        "Continue Conversation" button                     │
    │         → navigates back to feature page                  │
    └──────────────────────────────────────────────────────────┘
```

### 4.3 Redirect Rules

| Scenario | From | To | Condition |
|---|---|---|---|
| Authenticated user visits public page | `/`, `/login`, `/signup` | `/dashboard` | User has valid Firebase session |
| Unauthenticated user visits protected page | Any protected route | `/login?redirect={path}` | No valid Firebase session |
| Post-login redirect | `/login` | `?redirect` param or `/dashboard` | After successful authentication |
| Invalid template ID | `/dochub/invalid_id` | `/dochub` | `templateId` not in `[legal_notice, rental_agreement, affidavit]` |
| Invalid chat ID | `/history/invalid_id` | `/history` | Conversation not found (404 from API) |
| Logout | Any page | `/` | User clicks "Logout" |
| 404 (unknown route) | Any invalid path | `/dashboard` (if authed) or `/` (if not) | Route not found in router config |

---

## 5. Error Handling

### Frontend Error Handling

| Error Type | Handling |
|---|---|
| **401 from API** | Axios interceptor catches → clears auth state → redirects to `/login` |
| **403 from API** | Display "Access Denied" toast notification |
| **404 from API** | Display "Not Found" message in the component |
| **413 from API** | Display file size error in Upload component |
| **422 from API** | Display validation errors inline on form fields |
| **500 from API** | Display generic error toast: "Something went wrong. Please try again." |
| **Network Error** | Display offline banner: "Unable to connect to server" |

### Backend Error Handling

| Error Type | HTTP Code | Response |
|---|---|---|
| **Invalid Firebase token** | `401` | `{ "detail": "Invalid or expired authentication token", "code": "AUTH_INVALID_TOKEN" }` |
| **Missing Firebase token** | `401` | `{ "detail": "Authentication required", "code": "AUTH_MISSING_TOKEN" }` |
| **Resource not found** | `404` | `{ "detail": "Resource not found", "code": "NOT_FOUND" }` |
| **Resource belongs to another user** | `404` | `{ "detail": "Resource not found", "code": "NOT_FOUND" }` *(intentionally 404, not 403, to prevent enumeration)* |
| **Validation error** | `422` | `{ "detail": [{ "field": "name", "message": "Name is required" }], "code": "VALIDATION_ERROR" }` |
| **File too large** | `413` | `{ "detail": "File exceeds maximum size of 10MB", "code": "FILE_TOO_LARGE" }` |
| **Unsupported file type** | `400` | `{ "detail": "Unsupported file type. Allowed: pdf, docx, txt", "code": "INVALID_FILE_TYPE" }` |
| **Upload not ready** | `409` | `{ "detail": "Document is still processing", "code": "UPLOAD_NOT_READY" }` |
| **Gemini API error** | `502` | `{ "detail": "AI service temporarily unavailable", "code": "AI_SERVICE_ERROR" }` |
| **Database error** | `500` | `{ "detail": "Internal server error", "code": "INTERNAL_ERROR" }` |

---

### Backend Route Summary Table

| # | Method | Path | Auth | Description |
|---|---|---|---|---|
| 1 | POST | `/api/auth/register` | Yes | Register new user in local DB |
| 2 | POST | `/api/auth/login` | Yes | Record login, return profile |
| 3 | GET | `/api/auth/me` | Yes | Get current user profile |
| 4 | POST | `/api/chat/send` | Yes | Send message, get AI response |
| 5 | GET | `/api/chat/conversations` | Yes | List user's conversations |
| 6 | GET | `/api/chat/conversations/{id}` | Yes | Get conversation with messages |
| 7 | DELETE | `/api/chat/conversations/{id}` | Yes | Soft-delete conversation |
| 8 | POST | `/api/upload/file` | Yes | Upload document file |
| 9 | POST | `/api/upload/{id}/chat` | Yes | Chat with uploaded document |
| 10 | GET | `/api/upload/list` | Yes | List user's uploads |
| 11 | DELETE | `/api/upload/{id}` | Yes | Delete upload + embeddings |
| 12 | GET | `/api/documents/templates` | Yes | Get available templates |
| 13 | POST | `/api/documents/generate` | Yes | Generate document from template |
| 14 | POST | `/api/documents/{id}/export` | Yes | Export document as PDF/DOCX |
| 15 | GET | `/api/documents/list` | Yes | List user's documents |
| 16 | GET | `/api/documents/{id}` | Yes | Get specific document |
| 17 | DELETE | `/api/documents/{id}` | Yes | Delete document |
| 18 | POST | `/api/counter/generate` | Yes | Generate counter-arguments |
| 19 | GET | `/api/counter/list` | Yes | List saved counter-arguments |
| 20 | GET | `/api/counter/{id}` | Yes | Get specific counter-argument |
| 21 | DELETE | `/api/counter/{id}` | Yes | Delete counter-argument |
| 22 | GET | `/api/profile` | Yes | Get profile with stats |
| 23 | PUT | `/api/profile` | Yes | Update name/preferences |
| 24 | GET | `/api/history` | Yes | Get unified chat history |
| 25 | GET | `/api/history/search` | Yes | Search chat history |
| 26 | DELETE | `/api/history/{id}` | Yes | Delete history item |

**Total: 26 API endpoints across 7 route groups**

---

> **End of Document** — ROUTES.md v1.0
