# NYAAY AI — API Specification

> **Version:** 1.0
> **Date:** 2026-06-23
> **Author:** Ansh Darji
> **Status:** Final
> **References:** [ROUTES.md](./ROUTES.md), [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md)

---

## Standard Conventions

### Base URL

```
http://localhost:8000/api
```

### Authentication

All endpoints except `/api/auth/register` and `/api/auth/login` require a Firebase ID token:

```
Authorization: Bearer <firebase_id_token>
```

### Standard Success Response

```json
{
  "success": true,
  "data": { ... }
}
```

### Standard Paginated Response

```json
{
  "success": true,
  "data": [ ... ],
  "pagination": {
    "total": 42,
    "offset": 0,
    "limit": 20,
    "has_more": true
  }
}
```

### Standard Error Response

```json
{
  "success": false,
  "error": {
    "code": "error_code_string",
    "message": "Human-readable error message"
  }
}
```

### Pagination Parameters

| Parameter | Type | Default | Max | Description |
|-----------|------|---------|-----|-------------|
| `offset` | integer | 0 | — | Number of records to skip |
| `limit` | integer | 20 | 50 | Number of records to return |

### Rate Limit Headers

Every response includes:
```
X-RateLimit-Limit: 20
X-RateLimit-Remaining: 18
X-RateLimit-Reset: 1719100800
```

---

## 1. Auth Endpoints (`/api/auth`)

### POST `/api/auth/register`

Register a new user after Firebase signup.

| Property | Value |
|----------|-------|
| **Auth** | Not required (token in body) |
| **Rate Limit** | 5/min per IP |

**Request Body:**
```json
{
  "id_token": "string (required) — Firebase ID token",
  "name": "string (required) — Display name, 1-100 chars",
  "role": "string (required) — One of: citizen, student, lawyer"
}
```

**Success Response (201):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "firebase_uid": "abc123",
    "email": "user@example.com",
    "name": "Ansh Darji",
    "role": "student",
    "preferences": {},
    "created_at": "2026-06-23T10:00:00Z"
  }
}
```

**Error Responses:**

| Status | Code | When |
|--------|------|------|
| 400 | `invalid_token` | Firebase token is invalid or expired |
| 400 | `invalid_role` | Role is not citizen, student, or lawyer |
| 400 | `missing_fields` | Required fields are missing |
| 409 | `user_exists` | User with this Firebase UID already registered |
| 429 | `rate_limit_exceeded` | Too many requests |

---

### POST `/api/auth/login`

Verify Firebase token and return user profile. Creates user record on first Google login.

| Property | Value |
|----------|-------|
| **Auth** | Not required (token in body) |
| **Rate Limit** | 5/min per IP |

**Request Body:**
```json
{
  "id_token": "string (required) — Firebase ID token"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "firebase_uid": "abc123",
    "email": "user@example.com",
    "name": "Ansh Darji",
    "role": "student",
    "preferences": {"theme": "dark"},
    "created_at": "2026-06-23T10:00:00Z",
    "last_login": "2026-06-23T15:30:00Z"
  }
}
```

**Error Responses:**

| Status | Code | When |
|--------|------|------|
| 400 | `invalid_token` | Firebase token is invalid or expired |
| 404 | `user_not_found` | No user record (first Google login — frontend should prompt role selection and call /register) |
| 429 | `rate_limit_exceeded` | Too many requests |

---

### GET `/api/auth/me`

Get current authenticated user's profile.

| Property | Value |
|----------|-------|
| **Auth** | Required |
| **Rate Limit** | 30/min per user |

**Success Response (200):** Same as login response.

**Error Responses:**

| Status | Code | When |
|--------|------|------|
| 401 | `unauthorized` | Missing or invalid token |

---

## 2. Chat Endpoints (`/api/chat`) — Know Your Kanoon

### POST `/api/chat/conversations`

Create a new Know Your Kanoon conversation.

| Property | Value |
|----------|-------|
| **Auth** | Required |
| **Rate Limit** | 20/min per user |

**Request Body:**
```json
{
  "title": "string (optional) — Auto-generated if omitted"
}
```

**Success Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "uuid-string",
    "title": "New Conversation",
    "feature_type": "know_kanoon",
    "created_at": "2026-06-23T10:00:00Z",
    "updated_at": "2026-06-23T10:00:00Z",
    "messages": []
  }
}
```

---

### POST `/api/chat/conversations/:conversationId/messages`

Send a message and receive an AI response (Know Your Kanoon).

| Property | Value |
|----------|-------|
| **Auth** | Required |
| **Rate Limit** | 20/min per user |
| **Timeout** | 30s (Gemini API call) |

**URL Parameters:**
- `conversationId` (string, required) — UUID of the conversation

**Request Body:**
```json
{
  "content": "string (required) — User's question, 1-5000 chars"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "user_message": {
      "id": 1,
      "role": "user",
      "content": "What does Section 302 of BNS say?",
      "created_at": "2026-06-23T10:01:00Z"
    },
    "ai_message": {
      "id": 2,
      "role": "assistant",
      "content": "Section 302 of the Bharatiya Nyaya Sanhita (BNS) deals with...\n\n⚖️ *This is AI-generated information, not legal advice. Consult a qualified lawyer for legal decisions.*",
      "citations": [
        {
          "source": "Bharatiya Nyaya Sanhita",
          "section": "302",
          "relevance": "direct"
        }
      ],
      "created_at": "2026-06-23T10:01:05Z"
    }
  }
}
```

**Error Responses:**

| Status | Code | When |
|--------|------|------|
| 400 | `empty_message` | Content is empty or whitespace |
| 400 | `message_too_long` | Content exceeds 5000 chars |
| 404 | `conversation_not_found` | Conversation doesn't exist or doesn't belong to user |
| 429 | `rate_limit_exceeded` | Too many requests |
| 503 | `ai_unavailable` | Gemini API is down or rate limited (after retries) |
| 504 | `ai_timeout` | Gemini API timed out (after retries) |

---

### GET `/api/chat/conversations`

List user's conversations.

| Property | Value |
|----------|-------|
| **Auth** | Required |
| **Rate Limit** | 30/min per user |

**Query Parameters:**
- `offset` (integer, default: 0)
- `limit` (integer, default: 20, max: 50)
- `feature_type` (string, optional) — Filter by: know_kanoon, upload_chat

**Success Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid-string",
      "title": "Section 302 BNS Query",
      "feature_type": "know_kanoon",
      "created_at": "2026-06-23T10:00:00Z",
      "updated_at": "2026-06-23T10:05:00Z",
      "message_count": 4
    }
  ],
  "pagination": {
    "total": 15,
    "offset": 0,
    "limit": 20,
    "has_more": false
  }
}
```

---

### GET `/api/chat/conversations/:conversationId`

Get a conversation with all messages.

| Property | Value |
|----------|-------|
| **Auth** | Required |
| **Rate Limit** | 30/min per user |

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "uuid-string",
    "title": "Section 302 BNS Query",
    "feature_type": "know_kanoon",
    "created_at": "2026-06-23T10:00:00Z",
    "messages": [
      {
        "id": 1,
        "role": "user",
        "content": "What does Section 302 of BNS say?",
        "citations": null,
        "created_at": "2026-06-23T10:01:00Z"
      },
      {
        "id": 2,
        "role": "assistant",
        "content": "Section 302 of BNS deals with...",
        "citations": [{"source": "BNS", "section": "302", "relevance": "direct"}],
        "created_at": "2026-06-23T10:01:05Z"
      }
    ]
  }
}
```

**Error Responses:**

| Status | Code | When |
|--------|------|------|
| 404 | `conversation_not_found` | Not found or not owned by user |

---

### DELETE `/api/chat/conversations/:conversationId`

Delete a conversation and all its messages.

| Property | Value |
|----------|-------|
| **Auth** | Required |
| **Rate Limit** | 30/min per user |

**Success Response (200):**
```json
{
  "success": true,
  "data": { "deleted": true }
}
```

---

## 3. Upload Endpoints (`/api/upload`) — Upload & Chat

### POST `/api/upload/files`

Upload a document for analysis.

| Property | Value |
|----------|-------|
| **Auth** | Required |
| **Rate Limit** | 5/min per user |
| **Content-Type** | `multipart/form-data` |
| **Max Size** | 10 MB |

**Request Body (multipart):**
- `file` (file, required) — PDF, DOCX, or TXT file

**Success Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "uuid-string",
    "original_name": "rental_agreement.pdf",
    "file_type": "pdf",
    "file_size": 245760,
    "page_count": 12,
    "status": "ready",
    "conversation_id": "uuid-string",
    "created_at": "2026-06-23T10:00:00Z"
  }
}
```

**Error Responses:**

| Status | Code | When |
|--------|------|------|
| 400 | `unsupported_format` | File is not PDF, DOCX, or TXT |
| 400 | `invalid_file_content` | MIME type doesn't match extension |
| 400 | `too_many_pages` | PDF exceeds 300 pages |
| 400 | `no_text_content` | Cannot extract text (scanned/image PDF) |
| 413 | `file_too_large` | File exceeds 10 MB |
| 429 | `rate_limit_exceeded` | Too many requests |
| 500 | `processing_error` | Text extraction or embedding failed |

---

### POST `/api/upload/:uploadId/chat`

Chat with an uploaded document.

| Property | Value |
|----------|-------|
| **Auth** | Required |
| **Rate Limit** | 15/min per user |
| **Timeout** | 30s (Gemini API call) |

**Request Body:**
```json
{
  "content": "string (required) — User's question about the document, 1-5000 chars"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "user_message": {
      "id": 5,
      "role": "user",
      "content": "What are the termination clauses?",
      "created_at": "2026-06-23T10:05:00Z"
    },
    "ai_message": {
      "id": 6,
      "role": "assistant",
      "content": "Based on the uploaded document, the termination clauses are found in Section 8...\n\n⚖️ *This is AI-generated information, not legal advice.*",
      "citations": [
        {"source": "rental_agreement.pdf", "page": 5, "section": "8", "relevance": "direct"}
      ],
      "created_at": "2026-06-23T10:05:08Z"
    }
  }
}
```

**Error Responses:**

| Status | Code | When |
|--------|------|------|
| 400 | `upload_not_ready` | Upload status is 'processing' or 'error' |
| 404 | `upload_not_found` | Upload not found or not owned by user |
| 503 | `ai_unavailable` | Gemini API unavailable |

---

### GET `/api/upload/files`

List user's uploaded files.

| Property | Value |
|----------|-------|
| **Auth** | Required |
| **Rate Limit** | 30/min per user |

**Query Parameters:** `offset`, `limit`

**Success Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid-string",
      "original_name": "rental_agreement.pdf",
      "file_type": "pdf",
      "file_size": 245760,
      "page_count": 12,
      "status": "ready",
      "created_at": "2026-06-23T10:00:00Z"
    }
  ],
  "pagination": { "total": 3, "offset": 0, "limit": 20, "has_more": false }
}
```

---

### DELETE `/api/upload/files/:uploadId`

Delete an upload, its ChromaDB collection, and the file from disk.

| Property | Value |
|----------|-------|
| **Auth** | Required |
| **Rate Limit** | 30/min per user |

**Success Response (200):**
```json
{ "success": true, "data": { "deleted": true } }
```

---

## 4. Document Endpoints (`/api/documents`) — DocHub

### GET `/api/documents/templates`

List available document templates.

| Property | Value |
|----------|-------|
| **Auth** | Required |
| **Rate Limit** | 30/min per user |

**Success Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "legal_notice",
      "name": "Legal Notice",
      "description": "A formal notice sent to a party demanding action or compliance under law.",
      "fields": [
        {"name": "sender_name", "label": "Sender Name", "type": "text", "required": true},
        {"name": "sender_address", "label": "Sender Address", "type": "textarea", "required": true},
        {"name": "recipient_name", "label": "Recipient Name", "type": "text", "required": true},
        {"name": "recipient_address", "label": "Recipient Address", "type": "textarea", "required": true},
        {"name": "subject", "label": "Subject of Notice", "type": "text", "required": true},
        {"name": "facts", "label": "Statement of Facts", "type": "textarea", "required": true},
        {"name": "demand", "label": "Demand / Relief Sought", "type": "textarea", "required": true},
        {"name": "deadline_days", "label": "Compliance Deadline (days)", "type": "number", "required": true}
      ]
    },
    {
      "id": "rental_agreement",
      "name": "Rental Agreement",
      "description": "A lease agreement between landlord and tenant for residential or commercial property.",
      "fields": [
        {"name": "landlord_name", "label": "Landlord Name", "type": "text", "required": true},
        {"name": "tenant_name", "label": "Tenant Name", "type": "text", "required": true},
        {"name": "property_address", "label": "Property Address", "type": "textarea", "required": true},
        {"name": "rent_amount", "label": "Monthly Rent (₹)", "type": "number", "required": true},
        {"name": "security_deposit", "label": "Security Deposit (₹)", "type": "number", "required": true},
        {"name": "lease_duration_months", "label": "Lease Duration (months)", "type": "number", "required": true},
        {"name": "start_date", "label": "Lease Start Date", "type": "date", "required": true}
      ]
    },
    {
      "id": "affidavit",
      "name": "Affidavit",
      "description": "A sworn statement of facts made voluntarily under oath.",
      "fields": [
        {"name": "deponent_name", "label": "Deponent Name", "type": "text", "required": true},
        {"name": "deponent_age", "label": "Deponent Age", "type": "number", "required": true},
        {"name": "deponent_address", "label": "Deponent Address", "type": "textarea", "required": true},
        {"name": "purpose", "label": "Purpose of Affidavit", "type": "text", "required": true},
        {"name": "statements", "label": "Statements of Fact", "type": "textarea", "required": true},
        {"name": "location", "label": "Place of Execution", "type": "text", "required": true}
      ]
    }
  ]
}
```

---

### POST `/api/documents/generate`

Generate a legal document from a template.

| Property | Value |
|----------|-------|
| **Auth** | Required |
| **Rate Limit** | 10/min per user |
| **Timeout** | 30s |

**Request Body:**
```json
{
  "template_id": "string (required) — legal_notice, rental_agreement, or affidavit",
  "fields": {
    "sender_name": "string",
    "recipient_name": "string",
    "...": "..."
  }
}
```

**Success Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "uuid-string",
    "title": "Legal Notice - Ansh Darji",
    "template_type": "legal_notice",
    "content": "LEGAL NOTICE\n\nTo,\nMr. Recipient...\n\n...",
    "doc_type": "generated",
    "created_at": "2026-06-23T10:00:00Z"
  }
}
```

**Error Responses:**

| Status | Code | When |
|--------|------|------|
| 400 | `invalid_template` | Template ID not recognized |
| 400 | `missing_fields` | Required template fields are missing |
| 503 | `ai_unavailable` | Gemini API unavailable |

---

### POST `/api/documents/:documentId/export`

Export a generated document as PDF or DOCX.

| Property | Value |
|----------|-------|
| **Auth** | Required |
| **Rate Limit** | 10/min per user |

**Request Body:**
```json
{
  "format": "string (required) — pdf or docx",
  "content": "string (optional) — Updated content if user edited the document"
}
```

**Success Response (200):**
- Content-Type: `application/pdf` or `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- Content-Disposition: `attachment; filename="Legal_Notice_2026-06-23.pdf"`
- Body: Binary file content

**Error Responses:**

| Status | Code | When |
|--------|------|------|
| 400 | `invalid_format` | Format is not pdf or docx |
| 404 | `document_not_found` | Document not found or not owned by user |

---

### GET `/api/documents`

List user's saved documents.

| Property | Value |
|----------|-------|
| **Auth** | Required |
| **Rate Limit** | 30/min per user |

**Query Parameters:** `offset`, `limit`, `template_type` (optional filter)

**Success Response (200):** Paginated list of document summaries (id, title, template_type, doc_type, created_at).

---

### GET `/api/documents/:documentId`

Get a specific document with full content.

| Property | Value |
|----------|-------|
| **Auth** | Required |
| **Rate Limit** | 30/min per user |

---

### DELETE `/api/documents/:documentId`

Delete a document and its exported file (if any).

| Property | Value |
|----------|-------|
| **Auth** | Required |
| **Rate Limit** | 30/min per user |

---

## 5. Counter Argument Endpoints (`/api/counter`)

### POST `/api/counter/generate`

Generate counter-arguments for a legal position.

| Property | Value |
|----------|-------|
| **Auth** | Required |
| **Rate Limit** | 10/min per user |
| **Timeout** | 30s |

**Request Body:**
```json
{
  "argument": "string (required) — The legal argument or position, 10-5000 chars",
  "save": "boolean (optional, default: true) — Whether to save the result"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "uuid-string",
    "input_argument": "The tenant has the right to terminate the lease...",
    "result": {
      "opposing_viewpoints": [
        {
          "title": "Contractual Obligation Override",
          "argument": "While the tenant argues for termination rights...",
          "legal_basis": "Section 106, Transfer of Property Act",
          "strength": "strong"
        }
      ],
      "legal_rebuttals": [
        {
          "title": "Notice Period Non-Compliance",
          "argument": "The tenant failed to provide the mandatory...",
          "legal_basis": "Section 111, Transfer of Property Act",
          "strength": "moderate"
        }
      ],
      "alternative_interpretations": [
        {
          "title": "Constructive Eviction Defense",
          "argument": "An alternative reading suggests...",
          "legal_basis": "Case: Badri Narain v. Rameshwar Dayal (1951)",
          "strength": "moderate"
        }
      ],
      "strategic_perspectives": [
        {
          "title": "Negotiated Exit Strategy",
          "argument": "Rather than litigation, consider...",
          "legal_basis": null,
          "strength": "advisory"
        }
      ],
      "disclaimer": "⚖️ This is AI-generated information, not legal advice. Consult a qualified lawyer for legal decisions."
    },
    "created_at": "2026-06-23T10:00:00Z"
  }
}
```

**Error Responses:**

| Status | Code | When |
|--------|------|------|
| 400 | `argument_too_short` | Argument is less than 10 characters |
| 400 | `argument_too_long` | Argument exceeds 5000 characters |
| 503 | `ai_unavailable` | Gemini API unavailable |

---

### GET `/api/counter`

List saved counter-arguments.

| Property | Value |
|----------|-------|
| **Auth** | Required |
| **Rate Limit** | 30/min per user |

**Query Parameters:** `offset`, `limit`

**Success Response (200):** Paginated list with id, input_argument (truncated to 200 chars), created_at.

---

### GET `/api/counter/:id`

Get a specific counter-argument with full result.

---

### DELETE `/api/counter/:id`

Delete a saved counter-argument.

---

## 6. Profile Endpoints (`/api/profile`)

### GET `/api/profile`

Get current user's profile.

| Property | Value |
|----------|-------|
| **Auth** | Required |
| **Rate Limit** | 30/min per user |

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "user@example.com",
    "name": "Ansh Darji",
    "role": "student",
    "preferences": { "theme": "dark" },
    "created_at": "2026-06-23T10:00:00Z",
    "last_login": "2026-06-23T15:00:00Z",
    "stats": {
      "total_conversations": 12,
      "total_uploads": 3,
      "total_documents": 5,
      "total_counter_args": 2
    }
  }
}
```

---

### PUT `/api/profile`

Update user profile.

| Property | Value |
|----------|-------|
| **Auth** | Required |
| **Rate Limit** | 30/min per user |

**Request Body:**
```json
{
  "name": "string (optional) — 1-100 chars",
  "role": "string (optional) — citizen, student, or lawyer",
  "preferences": {
    "theme": "string (optional) — light or dark"
  }
}
```

**Success Response (200):** Updated profile object.

**Error Responses:**

| Status | Code | When |
|--------|------|------|
| 400 | `invalid_role` | Role is not citizen, student, or lawyer |
| 400 | `invalid_name` | Name is empty or exceeds 100 chars |

---

## 7. History Endpoints (`/api/history`)

### GET `/api/history`

Get unified activity history across all features.

| Property | Value |
|----------|-------|
| **Auth** | Required |
| **Rate Limit** | 30/min per user |

**Query Parameters:** `offset`, `limit`

**Success Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid-string",
      "type": "conversation",
      "feature": "know_kanoon",
      "title": "Section 302 BNS Query",
      "created_at": "2026-06-23T10:00:00Z",
      "updated_at": "2026-06-23T10:05:00Z"
    },
    {
      "id": "uuid-string",
      "type": "upload",
      "feature": "upload_chat",
      "title": "rental_agreement.pdf",
      "created_at": "2026-06-23T09:00:00Z",
      "updated_at": "2026-06-23T09:15:00Z"
    },
    {
      "id": "uuid-string",
      "type": "document",
      "feature": "dochub",
      "title": "Legal Notice - Ansh Darji",
      "created_at": "2026-06-23T08:00:00Z",
      "updated_at": null
    },
    {
      "id": "uuid-string",
      "type": "counter_argument",
      "feature": "counter",
      "title": "Tenant termination rights...",
      "created_at": "2026-06-23T07:00:00Z",
      "updated_at": null
    }
  ],
  "pagination": { "total": 22, "offset": 0, "limit": 20, "has_more": true }
}
```

---

### GET `/api/history/search`

Search across all history by keyword.

| Property | Value |
|----------|-------|
| **Auth** | Required |
| **Rate Limit** | 30/min per user |

**Query Parameters:**
- `q` (string, required) — Search keyword, min 2 chars
- `offset`, `limit`

**Success Response (200):** Same format as GET `/api/history`, filtered by keyword match in titles and content.

---

### DELETE `/api/history/:id`

Delete a specific history item (conversation, upload, document, or counter-argument).

| Property | Value |
|----------|-------|
| **Auth** | Required |
| **Rate Limit** | 30/min per user |

**Query Parameters:**
- `type` (string, required) — One of: conversation, upload, document, counter_argument

**Success Response (200):**
```json
{ "success": true, "data": { "deleted": true } }
```

---

## 8. Gemini Failure Handling Summary

All AI-powered endpoints follow this failure handling strategy:

| Scenario | Backend Behavior | HTTP Response | User-Facing Message |
|----------|-----------------|:------------:|---------------------|
| Gemini returns normally | Return AI response | 200 | — |
| Gemini rate limited (429) | Retry 3× with backoff (1s, 2s, 4s) | 503 | "Our AI service is temporarily busy. Please try again in a moment." |
| Gemini server error (500/503) | Retry 3× with backoff | 503 | "Our AI service is temporarily unavailable. Please try again shortly." |
| Gemini timeout (30s) | Retry 3× with backoff | 504 | "The request took too long. Please try a shorter question." |
| Gemini content filtered | No retry | 422 | "Your request could not be processed due to content restrictions." |
| All retries exhausted | Log error, return failure | 503 | "Our AI service is currently unavailable. Please try again later." |
| Invalid Gemini response | No retry | 502 | "We couldn't generate a response. Please rephrase your question." |

---

## 9. Rate Limiting Summary

| Endpoint Group | Limit | Key |
|---------------|-------|-----|
| `POST /api/auth/*` | 5/min | IP address |
| `POST /api/chat/*/messages` | 20/min | User ID |
| `POST /api/upload/files` | 5/min | User ID |
| `POST /api/upload/*/chat` | 15/min | User ID |
| `POST /api/documents/generate` | 10/min | User ID |
| `POST /api/documents/*/export` | 10/min | User ID |
| `POST /api/counter/generate` | 10/min | User ID |
| `GET /api/*` (reads) | 30/min | User ID |
| `DELETE /api/*` | 30/min | User ID |

---

> **Total Endpoints:** 26 | **Auth Required:** 23 | **Public:** 3 (register, login, — landing page is frontend-only)
