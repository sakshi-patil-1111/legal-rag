# NYAAY AI — Database Schema Design

> **Version:** 1.0  
> **Date:** 2026-06-23  
> **Status:** Draft  
> **Database Engine:** SQLite 3.x  
> **Document Type:** Technical Design Specification

---

## Table of Contents

1. [Overview](#1-overview)
2. [Design Principles](#2-design-principles)
3. [Entity Relationship Diagram](#3-entity-relationship-diagram)
4. [Table Definitions](#4-table-definitions)
   - 4.1 [users](#41-users)
   - 4.2 [conversations](#42-conversations)
   - 4.3 [messages](#43-messages)
   - 4.4 [documents](#44-documents)
   - 4.5 [uploads](#45-uploads)
   - 4.6 [counter_arguments](#46-counter_arguments)
5. [Index Strategy](#5-index-strategy)
6. [Data Ownership & Isolation](#6-data-ownership--isolation)
7. [Migration Strategy](#7-migration-strategy)
8. [Appendix: Full Schema Script](#8-appendix-full-schema-script)

---

## 1. Overview

This document defines the complete SQLite database schema for NYAAY AI — an AI-powered legal assistant for the Indian judiciary. The schema supports three user roles (Citizen, Student, Lawyer) and the following features:

| Feature | Primary Tables |
|---|---|
| Authentication & Profiles | `users` |
| Know Your Kanoon (Legal Q&A) | `conversations`, `messages` |
| Upload & Chat (Document Analysis) | `uploads`, `conversations`, `messages` |
| DocHub (Template Generation) | `documents` |
| Counter Argument Generator | `counter_arguments` |
| Chat History | `conversations`, `messages` |

**Key Constraints:**
- Firebase Auth manages authentication; `firebase_uid` is the canonical user identifier
- All UUIDs are stored as `TEXT` (SQLite has no native UUID type)
- JSON fields use SQLite's JSON1 extension for structured data
- Timestamps use ISO 8601 format in UTC (`YYYY-MM-DDTHH:MM:SSZ`)

---

## 2. Design Principles

| Principle | Implementation |
|---|---|
| **Firebase as Auth Source** | `users.firebase_uid` is the canonical identity; no passwords stored locally |
| **Data Isolation** | Every data table has a `user_id` FK — queries are always scoped per user |
| **Soft Delete Ready** | Tables use `is_active` or status fields; hard deletes cascade on FK |
| **JSON for Flexibility** | Semi-structured data (citations, preferences, results) stored as JSON TEXT |
| **UUID Primary Keys** | All entity tables use UUID v4 strings to prevent enumeration attacks |
| **Referential Integrity** | Foreign keys enforced with `PRAGMA foreign_keys = ON` |
| **Defensive Constraints** | CHECK constraints enforce enum values at the database level |

---

## 3. Entity Relationship Diagram

```
┌─────────────────────────┐
│         users            │
│─────────────────────────│
│ PK  firebase_uid  TEXT   │
│     email          TEXT   │
│     name           TEXT   │
│     role           TEXT   │
│     preferences    TEXT   │
│     created_at     TEXT   │
│     last_login     TEXT   │
└────────┬────────────────┘
         │
         │ 1
         │
         ├──────────────────────────────┬─────────────────────────┐
         │                              │                         │
         ▼ N                            ▼ N                       ▼ N
┌────────────────────────┐  ┌──────────────────────┐  ┌──────────────────────────┐
│     conversations       │  │      documents        │  │    counter_arguments      │
│────────────────────────│  │──────────────────────│  │──────────────────────────│
│ PK  id        TEXT(UUID)│  │ PK  id    TEXT(UUID)  │  │ PK  id        TEXT(UUID)  │
│ FK  user_id   TEXT      │  │ FK  user_id TEXT      │  │ FK  user_id   TEXT        │
│     title     TEXT      │  │ FK  conv_id TEXT NULL  │  │     input_argument TEXT   │
│     feature_type TEXT   │  │     title   TEXT       │  │     result_json    TEXT   │
│     created_at TEXT     │  │     template_type TEXT │  │     created_at     TEXT   │
│     updated_at TEXT     │  │     content  TEXT      │  └──────────────────────────┘
│     is_active  INTEGER  │  │     file_path TEXT     │
└────────┬───────────────┘  │     doc_type  TEXT     │
         │                  │     created_at TEXT     │
         │ 1                └──────────────────────┘
         │
         ├──────────────────────┐
         │                      │
         ▼ N                    ▼ N
┌────────────────────────┐  ┌──────────────────────────┐
│       messages          │  │         uploads           │
│────────────────────────│  │──────────────────────────│
│ PK  id      INTEGER     │  │ PK  id        TEXT(UUID)  │
│ FK  conv_id TEXT        │  │ FK  user_id   TEXT        │
│     role    TEXT        │  │ FK  conv_id   TEXT NULL   │
│     content TEXT        │  │     original_name TEXT    │
│     citations TEXT      │  │     file_path     TEXT    │
│     created_at TEXT     │  │     file_type     TEXT    │
└────────────────────────┘  │     file_size     INTEGER │
                            │     page_count    INTEGER │
                            │     chroma_collection TEXT│
                            │     status         TEXT   │
                            │     created_at     TEXT   │
                            └──────────────────────────┘
```

**Relationship Summary:**

| Relationship | Cardinality | FK Column | ON DELETE |
|---|---|---|---|
| users → conversations | 1:N | `conversations.user_id` | CASCADE |
| users → documents | 1:N | `documents.user_id` | CASCADE |
| users → uploads | 1:N | `uploads.user_id` | CASCADE |
| users → counter_arguments | 1:N | `counter_arguments.user_id` | CASCADE |
| conversations → messages | 1:N | `messages.conversation_id` | CASCADE |
| conversations → documents | 1:N (optional) | `documents.conversation_id` | SET NULL |
| conversations → uploads | 1:N (optional) | `uploads.conversation_id` | SET NULL |

---

## 4. Table Definitions

### 4.1 `users`

**Purpose:** Stores user profile data synchronized from Firebase Auth. Acts as the local identity anchor for all data ownership.

| Column | Type | Constraints | Default | Description |
|---|---|---|---|---|
| `firebase_uid` | TEXT | PRIMARY KEY, NOT NULL | — | Firebase Auth UID (canonical identifier) |
| `email` | TEXT | NOT NULL, UNIQUE | — | User's email address |
| `name` | TEXT | NOT NULL | — | Display name |
| `role` | TEXT | NOT NULL, CHECK | — | One of: `citizen`, `student`, `lawyer` |
| `preferences` | TEXT | — | `'{}'` | JSON object for UI preferences, notification settings, etc. |
| `created_at` | TEXT | NOT NULL | `CURRENT_TIMESTAMP` | Account creation timestamp (ISO 8601 UTC) |
| `last_login` | TEXT | NOT NULL | `CURRENT_TIMESTAMP` | Last successful login timestamp |

**CHECK Constraints:**
- `role IN ('citizen', 'student', 'lawyer')` — Enforces the three valid user roles

**JSON Schema for `preferences`:**
```json
{
  "theme": "light | dark",
  "language": "en | hi",
  "notifications": true,
  "default_feature": "know_kanoon | upload_chat | dochub | counter_arg"
}
```

**SQL:**
```sql
CREATE TABLE IF NOT EXISTS users (
    firebase_uid    TEXT    PRIMARY KEY NOT NULL,
    email           TEXT    NOT NULL UNIQUE,
    name            TEXT    NOT NULL,
    role            TEXT    NOT NULL CHECK (role IN ('citizen', 'student', 'lawyer')),
    preferences     TEXT    DEFAULT '{}',
    created_at      TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    last_login      TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);
```

**Indexes:**
```sql
-- Fast lookup by email (login flow, duplicate checks)
CREATE UNIQUE INDEX idx_users_email ON users(email);
```

> **Note:** `firebase_uid` is the PK and is already indexed by SQLite. The email index supports lookup during registration checks and profile search.

---

### 4.2 `conversations`

**Purpose:** Tracks all chat-based interactions across features (Know Your Kanoon, Upload & Chat, Counter Arguments). Each conversation is a logical grouping of messages.

| Column | Type | Constraints | Default | Description |
|---|---|---|---|---|
| `id` | TEXT | PRIMARY KEY, NOT NULL | — | UUID v4 string |
| `user_id` | TEXT | NOT NULL, FK → users | — | Owner of this conversation |
| `title` | TEXT | NOT NULL | `'New Conversation'` | Auto-generated or user-set title |
| `feature_type` | TEXT | NOT NULL, CHECK | — | Feature context: `know_kanoon`, `upload_chat`, or `counter_arg` |
| `created_at` | TEXT | NOT NULL | `CURRENT_TIMESTAMP` | Conversation start time |
| `updated_at` | TEXT | NOT NULL | `CURRENT_TIMESTAMP` | Last message timestamp |
| `is_active` | INTEGER | NOT NULL, CHECK | `1` | Soft delete flag: 1 = active, 0 = archived/deleted |

**CHECK Constraints:**
- `feature_type IN ('know_kanoon', 'upload_chat', 'counter_arg')`
- `is_active IN (0, 1)` — SQLite boolean

**SQL:**
```sql
CREATE TABLE IF NOT EXISTS conversations (
    id              TEXT    PRIMARY KEY NOT NULL,
    user_id         TEXT    NOT NULL,
    title           TEXT    NOT NULL DEFAULT 'New Conversation',
    feature_type    TEXT    NOT NULL CHECK (feature_type IN ('know_kanoon', 'upload_chat', 'counter_arg')),
    created_at      TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at      TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    is_active       INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),

    FOREIGN KEY (user_id) REFERENCES users(firebase_uid) ON DELETE CASCADE
);
```

**Indexes:**
```sql
-- Primary query pattern: list conversations for a user, filtered by feature, ordered by recent
CREATE INDEX idx_conversations_user_feature ON conversations(user_id, feature_type, is_active);

-- Chat history listing: all active conversations for a user, sorted by updated_at
CREATE INDEX idx_conversations_user_updated ON conversations(user_id, updated_at DESC);
```

> **Index Rationale:**
> - `idx_conversations_user_feature` — The dashboard and feature pages always list conversations per user per feature. This composite index covers the WHERE clause and avoids full table scans.
> - `idx_conversations_user_updated` — Chat history page sorts by most recent activity. This index supports the ORDER BY without a filesort.

---

### 4.3 `messages`

**Purpose:** Stores individual messages within a conversation. Each message is either from the user or the AI assistant. Citations link back to legal sources retrieved via RAG.

| Column | Type | Constraints | Default | Description |
|---|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | — | Auto-incrementing message ID |
| `conversation_id` | TEXT | NOT NULL, FK → conversations | — | Parent conversation |
| `role` | TEXT | NOT NULL, CHECK | — | Message sender: `user` or `assistant` |
| `content` | TEXT | NOT NULL | — | Message text content (markdown supported) |
| `citations` | TEXT | — | `NULL` | JSON array of legal citations (assistant messages only) |
| `created_at` | TEXT | NOT NULL | `CURRENT_TIMESTAMP` | Message timestamp |

**CHECK Constraints:**
- `role IN ('user', 'assistant')`

**JSON Schema for `citations`:**
```json
[
  {
    "source": "Constitution of India",
    "section": "Article 21",
    "text": "No person shall be deprived of his life or personal liberty...",
    "relevance_score": 0.92,
    "chunk_id": "chroma_chunk_xyz"
  }
]
```

**SQL:**
```sql
CREATE TABLE IF NOT EXISTS messages (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT    NOT NULL,
    role            TEXT    NOT NULL CHECK (role IN ('user', 'assistant')),
    content         TEXT    NOT NULL,
    citations       TEXT    DEFAULT NULL,
    created_at      TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),

    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);
```

**Indexes:**
```sql
-- Fetch all messages in a conversation, ordered chronologically
CREATE INDEX idx_messages_conversation ON messages(conversation_id, created_at ASC);
```

> **Index Rationale:**
> - `idx_messages_conversation` — Every chat view fetches all messages for a conversation in chronological order. This composite index covers both the WHERE (conversation_id) and ORDER BY (created_at) clauses.
> - `id` uses INTEGER PRIMARY KEY AUTOINCREMENT for efficient sequential inserts and natural ordering within a conversation.

---

### 4.4 `documents`

**Purpose:** Stores documents generated via DocHub (Legal Notice, Rental Agreement, Affidavit). Tracks both the generated content and any exported file artifacts.

| Column | Type | Constraints | Default | Description |
|---|---|---|---|---|
| `id` | TEXT | PRIMARY KEY, NOT NULL | — | UUID v4 string |
| `user_id` | TEXT | NOT NULL, FK → users | — | Owner of this document |
| `conversation_id` | TEXT | FK → conversations, NULLABLE | `NULL` | Optional link to a chat conversation that generated this doc |
| `title` | TEXT | NOT NULL | — | Document title (user-provided or auto-generated) |
| `template_type` | TEXT | NOT NULL, CHECK | — | Template: `legal_notice`, `rental_agreement`, or `affidavit` |
| `content` | TEXT | NOT NULL | — | Full generated document content (markdown/HTML) |
| `file_path` | TEXT | — | `NULL` | Path to exported file on disk (PDF/DOCX), NULL if not exported |
| `doc_type` | TEXT | NOT NULL, CHECK | `'generated'` | Document lifecycle: `generated` or `exported` |
| `created_at` | TEXT | NOT NULL | `CURRENT_TIMESTAMP` | Document creation timestamp |

**CHECK Constraints:**
- `template_type IN ('legal_notice', 'rental_agreement', 'affidavit')` — Only 3 templates supported
- `doc_type IN ('generated', 'exported')`

**SQL:**
```sql
CREATE TABLE IF NOT EXISTS documents (
    id              TEXT    PRIMARY KEY NOT NULL,
    user_id         TEXT    NOT NULL,
    conversation_id TEXT    DEFAULT NULL,
    title           TEXT    NOT NULL,
    template_type   TEXT    NOT NULL CHECK (template_type IN ('legal_notice', 'rental_agreement', 'affidavit')),
    content         TEXT    NOT NULL,
    file_path       TEXT    DEFAULT NULL,
    doc_type        TEXT    NOT NULL DEFAULT 'generated' CHECK (doc_type IN ('generated', 'exported')),
    created_at      TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),

    FOREIGN KEY (user_id) REFERENCES users(firebase_uid) ON DELETE CASCADE,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE SET NULL
);
```

**Indexes:**
```sql
-- List user's documents filtered by template type
CREATE INDEX idx_documents_user_template ON documents(user_id, template_type);

-- List user's documents sorted by creation date (DocHub listing page)
CREATE INDEX idx_documents_user_created ON documents(user_id, created_at DESC);
```

> **Index Rationale:**
> - `idx_documents_user_template` — DocHub page filters documents by template type per user.
> - `idx_documents_user_created` — Document listing defaults to newest-first sort.
> - `conversation_id` FK uses `ON DELETE SET NULL` because a document should persist even if the originating conversation is deleted.

---

### 4.5 `uploads`

**Purpose:** Tracks files uploaded by users for the Upload & Chat feature. Manages file metadata, processing status, and the reference to the per-upload ChromaDB collection for vector search.

| Column | Type | Constraints | Default | Description |
|---|---|---|---|---|
| `id` | TEXT | PRIMARY KEY, NOT NULL | — | UUID v4 string |
| `user_id` | TEXT | NOT NULL, FK → users | — | Owner of this upload |
| `conversation_id` | TEXT | FK → conversations, NULLABLE | `NULL` | Associated conversation (set when chat begins) |
| `original_name` | TEXT | NOT NULL | — | Original filename as uploaded |
| `file_path` | TEXT | NOT NULL | — | Server-side storage path |
| `file_type` | TEXT | NOT NULL, CHECK | — | File format: `pdf`, `docx`, or `txt` |
| `file_size` | INTEGER | NOT NULL, CHECK | — | File size in bytes |
| `page_count` | INTEGER | — | `NULL` | Number of pages (NULL for TXT files) |
| `chroma_collection` | TEXT | — | `NULL` | ChromaDB collection name for this upload's embeddings |
| `status` | TEXT | NOT NULL, CHECK | `'processing'` | Processing pipeline status |
| `created_at` | TEXT | NOT NULL | `CURRENT_TIMESTAMP` | Upload timestamp |

**CHECK Constraints:**
- `file_type IN ('pdf', 'docx', 'txt')`
- `file_size > 0 AND file_size <= 10485760` — Max 10MB (10 × 1024 × 1024 bytes)
- `page_count IS NULL OR (page_count > 0 AND page_count <= 300)` — Max 300 pages
- `status IN ('processing', 'ready', 'error')`

**SQL:**
```sql
CREATE TABLE IF NOT EXISTS uploads (
    id                  TEXT    PRIMARY KEY NOT NULL,
    user_id             TEXT    NOT NULL,
    conversation_id     TEXT    DEFAULT NULL,
    original_name       TEXT    NOT NULL,
    file_path           TEXT    NOT NULL,
    file_type           TEXT    NOT NULL CHECK (file_type IN ('pdf', 'docx', 'txt')),
    file_size           INTEGER NOT NULL CHECK (file_size > 0 AND file_size <= 10485760),
    page_count          INTEGER DEFAULT NULL CHECK (page_count IS NULL OR (page_count > 0 AND page_count <= 300)),
    chroma_collection   TEXT    DEFAULT NULL,
    status              TEXT    NOT NULL DEFAULT 'processing' CHECK (status IN ('processing', 'ready', 'error')),
    created_at          TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),

    FOREIGN KEY (user_id) REFERENCES users(firebase_uid) ON DELETE CASCADE,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE SET NULL
);
```

**Indexes:**
```sql
-- List user's uploads (Upload & Chat page)
CREATE INDEX idx_uploads_user ON uploads(user_id, created_at DESC);

-- Filter uploads by processing status (background job polling)
CREATE INDEX idx_uploads_status ON uploads(status);

-- Lookup by chroma_collection name (RAG retrieval path)
CREATE INDEX idx_uploads_chroma ON uploads(chroma_collection);
```

> **Index Rationale:**
> - `idx_uploads_user` — Upload listing page shows all uploads per user, newest first.
> - `idx_uploads_status` — Background processing jobs query for `status = 'processing'` to find unfinished uploads.
> - `idx_uploads_chroma` — During RAG retrieval, the system maps a ChromaDB collection name back to the upload record for metadata.

---

### 4.6 `counter_arguments`

**Purpose:** Stores generated counter-argument results from the Counter Argument Generator feature. Each record represents a single generation run with the input argument and structured output across 4 categories.

| Column | Type | Constraints | Default | Description |
|---|---|---|---|---|
| `id` | TEXT | PRIMARY KEY, NOT NULL | — | UUID v4 string |
| `user_id` | TEXT | NOT NULL, FK → users | — | Owner of this result |
| `input_argument` | TEXT | NOT NULL | — | The original argument provided by the user |
| `result_json` | TEXT | NOT NULL | — | JSON object containing all 4 counter-argument categories |
| `created_at` | TEXT | NOT NULL | `CURRENT_TIMESTAMP` | Generation timestamp |

**JSON Schema for `result_json`:**
```json
{
  "opposing_viewpoints": [
    {
      "title": "...",
      "argument": "...",
      "legal_basis": "...",
      "strength": "strong | moderate | weak"
    }
  ],
  "legal_rebuttals": [
    {
      "title": "...",
      "argument": "...",
      "legal_basis": "...",
      "strength": "strong | moderate | weak"
    }
  ],
  "alternative_interpretations": [
    {
      "title": "...",
      "argument": "...",
      "legal_basis": "...",
      "strength": "strong | moderate | weak"
    }
  ],
  "strategic_perspectives": [
    {
      "title": "...",
      "argument": "...",
      "legal_basis": "...",
      "strength": "strong | moderate | weak"
    }
  ]
}
```

**SQL:**
```sql
CREATE TABLE IF NOT EXISTS counter_arguments (
    id              TEXT    PRIMARY KEY NOT NULL,
    user_id         TEXT    NOT NULL,
    input_argument  TEXT    NOT NULL,
    result_json     TEXT    NOT NULL,
    created_at      TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),

    FOREIGN KEY (user_id) REFERENCES users(firebase_uid) ON DELETE CASCADE
);
```

**Indexes:**
```sql
-- List user's counter-argument history (newest first)
CREATE INDEX idx_counter_args_user ON counter_arguments(user_id, created_at DESC);
```

> **Index Rationale:**
> - `idx_counter_args_user` — The counter-argument history page lists results per user sorted by most recent.

---

## 5. Index Strategy

### Complete Index Registry

| Index Name | Table | Columns | Type | Purpose |
|---|---|---|---|---|
| `idx_users_email` | users | `email` | UNIQUE | Email lookup during auth |
| `idx_conversations_user_feature` | conversations | `user_id, feature_type, is_active` | COMPOSITE | Feature-filtered conversation listing |
| `idx_conversations_user_updated` | conversations | `user_id, updated_at DESC` | COMPOSITE | Chat history sorted by recency |
| `idx_messages_conversation` | messages | `conversation_id, created_at ASC` | COMPOSITE | Chronological message retrieval |
| `idx_documents_user_template` | documents | `user_id, template_type` | COMPOSITE | Template-filtered document listing |
| `idx_documents_user_created` | documents | `user_id, created_at DESC` | COMPOSITE | Newest-first document listing |
| `idx_uploads_user` | uploads | `user_id, created_at DESC` | COMPOSITE | User's upload listing |
| `idx_uploads_status` | uploads | `status` | SINGLE | Background job status polling |
| `idx_uploads_chroma` | uploads | `chroma_collection` | SINGLE | ChromaDB collection → upload lookup |
| `idx_counter_args_user` | counter_arguments | `user_id, created_at DESC` | COMPOSITE | Counter-argument history listing |

### Index Design Guidelines

1. **Composite indexes follow query patterns** — Left-most columns match WHERE clauses, trailing columns match ORDER BY
2. **No over-indexing** — Each index has a specific, documented query that uses it
3. **DESC indexes for recency** — Most listing views show newest items first
4. **SQLite limitation** — SQLite doesn't support partial indexes in all versions; `is_active` is included in composite indexes instead

---

## 6. Data Ownership & Isolation

### Ownership Rules

| Rule | Implementation |
|---|---|
| **User owns all their data** | Every data table has `user_id` FK to `users.firebase_uid` |
| **No cross-user access** | All API queries MUST include `WHERE user_id = :current_user_id` |
| **Cascade on delete** | Deleting a user removes all their data (conversations, messages, documents, uploads, counter-arguments) |
| **Conversation isolation** | Messages belong to a conversation; deleting a conversation cascades to its messages |
| **Document preservation** | Documents survive conversation deletion (`ON DELETE SET NULL` on `conversation_id`) |
| **Upload preservation** | Uploads survive conversation deletion (`ON DELETE SET NULL` on `conversation_id`) |

### Backend Enforcement Pattern

```
# Pseudocode — Every data query MUST follow this pattern
def get_conversations(current_user_id: str, feature_type: str):
    query = """
        SELECT * FROM conversations
        WHERE user_id = :user_id
          AND feature_type = :feature_type
          AND is_active = 1
        ORDER BY updated_at DESC
    """
    # current_user_id is ALWAYS extracted from the verified Firebase token
    # NEVER from request parameters
```

### Security Rules

1. **`user_id` is NEVER client-supplied** — Always extracted from the verified Firebase Auth token on the backend
2. **No admin endpoints expose cross-user data** — V1 has no admin panel
3. **File paths are server-generated** — Clients never specify file storage paths
4. **ChromaDB collections are per-upload** — Named with UUID to prevent collection name collisions

---

## 7. Migration Strategy

### Initial Setup

The schema is applied via a single initialization script on first server start:

```
1. Check if database file exists
2. If not, create it and run the full schema script (Section 8)
3. Enable foreign keys: PRAGMA foreign_keys = ON
4. Enable WAL mode for concurrent reads: PRAGMA journal_mode = WAL
5. Set busy timeout: PRAGMA busy_timeout = 5000
```

### Version Tracking

```sql
-- Metadata table for schema versioning
CREATE TABLE IF NOT EXISTS schema_version (
    version     INTEGER PRIMARY KEY NOT NULL,
    applied_at  TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    description TEXT    NOT NULL
);

-- Initial version
INSERT INTO schema_version (version, description) VALUES (1, 'Initial schema — 6 core tables');
```

### Future Migration Process

| Step | Action |
|---|---|
| 1 | Create a migration script: `migrations/002_add_column.sql` |
| 2 | Each migration checks current version before applying |
| 3 | Wrap migrations in transactions for atomicity |
| 4 | Update `schema_version` after successful migration |
| 5 | Never modify existing migration files — only add new ones |

### Migration Script Template

```sql
-- Migration 002: Example — Add 'language' column to documents
-- Prerequisites: schema_version >= 1

BEGIN TRANSACTION;

-- Guard: only run if not already applied
SELECT CASE
    WHEN (SELECT MAX(version) FROM schema_version) >= 2
    THEN RAISE(ABORT, 'Migration 002 already applied')
END;

ALTER TABLE documents ADD COLUMN language TEXT DEFAULT 'en';

INSERT INTO schema_version (version, description)
VALUES (2, 'Add language column to documents');

COMMIT;
```

### SQLite-Specific Considerations

| Consideration | Approach |
|---|---|
| **No DROP COLUMN** (pre-3.35.0) | Use the 12-step ALTER TABLE process: create new table → copy data → drop old → rename |
| **No ADD CONSTRAINT** | CHECK constraints must be defined at table creation; use triggers as runtime guards for post-creation constraints |
| **WAL mode** | Enabled for concurrent read access from FastAPI async handlers |
| **Busy timeout** | Set to 5000ms to handle write contention under moderate load |
| **VACUUM** | Schedule periodic VACUUM to reclaim space after bulk deletes |

---

## 8. Appendix: Full Schema Script

```sql
-- ============================================================
-- NYAAY AI — Complete Database Schema
-- Version: 1.0
-- Date: 2026-06-23
-- Engine: SQLite 3.x
-- ============================================================

-- Enable required pragmas
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA busy_timeout = 5000;

-- ============================================================
-- TABLE: schema_version
-- ============================================================
CREATE TABLE IF NOT EXISTS schema_version (
    version     INTEGER PRIMARY KEY NOT NULL,
    applied_at  TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    description TEXT    NOT NULL
);

-- ============================================================
-- TABLE: users
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    firebase_uid    TEXT    PRIMARY KEY NOT NULL,
    email           TEXT    NOT NULL UNIQUE,
    name            TEXT    NOT NULL,
    role            TEXT    NOT NULL CHECK (role IN ('citizen', 'student', 'lawyer')),
    preferences     TEXT    DEFAULT '{}',
    created_at      TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    last_login      TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- ============================================================
-- TABLE: conversations
-- ============================================================
CREATE TABLE IF NOT EXISTS conversations (
    id              TEXT    PRIMARY KEY NOT NULL,
    user_id         TEXT    NOT NULL,
    title           TEXT    NOT NULL DEFAULT 'New Conversation',
    feature_type    TEXT    NOT NULL CHECK (feature_type IN ('know_kanoon', 'upload_chat', 'counter_arg')),
    created_at      TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at      TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    is_active       INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),

    FOREIGN KEY (user_id) REFERENCES users(firebase_uid) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_conversations_user_feature ON conversations(user_id, feature_type, is_active);
CREATE INDEX IF NOT EXISTS idx_conversations_user_updated ON conversations(user_id, updated_at DESC);

-- ============================================================
-- TABLE: messages
-- ============================================================
CREATE TABLE IF NOT EXISTS messages (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT    NOT NULL,
    role            TEXT    NOT NULL CHECK (role IN ('user', 'assistant')),
    content         TEXT    NOT NULL,
    citations       TEXT    DEFAULT NULL,
    created_at      TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),

    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id, created_at ASC);

-- ============================================================
-- TABLE: documents
-- ============================================================
CREATE TABLE IF NOT EXISTS documents (
    id              TEXT    PRIMARY KEY NOT NULL,
    user_id         TEXT    NOT NULL,
    conversation_id TEXT    DEFAULT NULL,
    title           TEXT    NOT NULL,
    template_type   TEXT    NOT NULL CHECK (template_type IN ('legal_notice', 'rental_agreement', 'affidavit')),
    content         TEXT    NOT NULL,
    file_path       TEXT    DEFAULT NULL,
    doc_type        TEXT    NOT NULL DEFAULT 'generated' CHECK (doc_type IN ('generated', 'exported')),
    created_at      TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),

    FOREIGN KEY (user_id) REFERENCES users(firebase_uid) ON DELETE CASCADE,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_documents_user_template ON documents(user_id, template_type);
CREATE INDEX IF NOT EXISTS idx_documents_user_created ON documents(user_id, created_at DESC);

-- ============================================================
-- TABLE: uploads
-- ============================================================
CREATE TABLE IF NOT EXISTS uploads (
    id                  TEXT    PRIMARY KEY NOT NULL,
    user_id             TEXT    NOT NULL,
    conversation_id     TEXT    DEFAULT NULL,
    original_name       TEXT    NOT NULL,
    file_path           TEXT    NOT NULL,
    file_type           TEXT    NOT NULL CHECK (file_type IN ('pdf', 'docx', 'txt')),
    file_size           INTEGER NOT NULL CHECK (file_size > 0 AND file_size <= 10485760),
    page_count          INTEGER DEFAULT NULL CHECK (page_count IS NULL OR (page_count > 0 AND page_count <= 300)),
    chroma_collection   TEXT    DEFAULT NULL,
    status              TEXT    NOT NULL DEFAULT 'processing' CHECK (status IN ('processing', 'ready', 'error')),
    created_at          TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),

    FOREIGN KEY (user_id) REFERENCES users(firebase_uid) ON DELETE CASCADE,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_uploads_user ON uploads(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_uploads_status ON uploads(status);
CREATE INDEX IF NOT EXISTS idx_uploads_chroma ON uploads(chroma_collection);

-- ============================================================
-- TABLE: counter_arguments
-- ============================================================
CREATE TABLE IF NOT EXISTS counter_arguments (
    id              TEXT    PRIMARY KEY NOT NULL,
    user_id         TEXT    NOT NULL,
    input_argument  TEXT    NOT NULL,
    result_json     TEXT    NOT NULL,
    created_at      TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),

    FOREIGN KEY (user_id) REFERENCES users(firebase_uid) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_counter_args_user ON counter_arguments(user_id, created_at DESC);

-- ============================================================
-- Record initial schema version
-- ============================================================
INSERT OR IGNORE INTO schema_version (version, description)
VALUES (1, 'Initial schema — 6 core tables');
```

---

> **End of Document** — DATABASE_SCHEMA.md v1.0
