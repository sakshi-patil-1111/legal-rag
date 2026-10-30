# NYAAY AI — PRD Revisions

> **Version:** 1.0
> **Date:** 2026-06-23
> **Applies to:** [PRD.md](./PRD.md) v1.0
> **Status:** Final — Changes Identified

---

## Summary

The existing PRD.md contains **14 issues** requiring correction. These stem from scope refinements made after the initial PRD was approved:

1. Researcher role removed (now 3 roles: Citizen, Student, Lawyer)
2. DocHub templates reduced from 5 to 3 (removed NDA, Power of Attorney)
3. Counter Argument categories reduced from 5 to 4 (removed Procedural Defenses)
4. Upload page limit (300 pages) was missing
5. Legal corpus strategy was undefined
6. Rate limiting was incorrectly listed as out of scope

---

## Issues & Corrections

### Issue 1: Executive Summary References Researchers

**Location:** Line 12
**Severity:** Medium

```diff
- **NYAAY AI** is an AI-powered legal assistant designed for the Indian judiciary ecosystem. It empowers citizens, students, researchers, and legal professionals to navigate Indian law...
+ **NYAAY AI** is an AI-powered legal assistant designed for the Indian judiciary ecosystem. It empowers citizens, students, and legal professionals to navigate Indian law...
```

---

### Issue 2: Problem Statement Lists Researchers

**Location:** Line 26
**Severity:** Medium

```diff
- - **Researchers** who need efficient search and synthesis across legal corpora.
(Remove this entire line)
```

---

### Issue 3: Persona 3 Is Researcher — Must Remove

**Location:** Lines 80–84
**Severity:** High

```diff
- ### Persona 3: Researcher (Dr. Mehra, 45, Legal Academic)
-
- - **Need:** Analyze patterns in Supreme Court judgments on environmental law.
- - **Pain:** Manual reading of hundreds of judgments.
- - **NYAAY AI Use:** Uploads a batch of judgments → asks for summarization and clause extraction → exports findings.
(Remove entire persona block. Renumber Persona 4 → Persona 3.)
```

---

### Issue 4: Auth Roles Include Researcher

**Location:** Line 124
**Severity:** High

```diff
- | User Roles | Citizen, Student, Researcher, Lawyer (selected at signup) |
+ | User Roles | Citizen, Student, Lawyer (selected at signup) |
```

---

### Issue 5: MVP Goal 3 Says "5 Templates"

**Location:** Line 49
**Severity:** Medium

```diff
- | 3 | Allow users to generate legal documents from templates | At least 5 templates available and exportable |
+ | 3 | Allow users to generate legal documents from templates | 3 templates available and exportable (Legal Notice, Rental Agreement, Affidavit) |
```

---

### Issue 6: DocHub Lists 5 Templates

**Location:** Line 222
**Severity:** High

```diff
- | Templates | Affidavit, Rental Agreement, NDA, Legal Notice, Power of Attorney |
+ | Templates | Legal Notice, Rental Agreement, Affidavit |
```

---

### Issue 7: DocHub Acceptance Criteria Says "All 5"

**Location:** Line 232
**Severity:** Medium

```diff
- - All 5 templates are available and functional.
+ - All 3 templates are available and functional.
```

---

### Issue 8: Counter Argument Has 5 Categories

**Location:** Line 247
**Severity:** Medium

```diff
- | Categories | Opposing arguments, Legal rebuttals, Procedural defenses, Alternative interpretations, Strategic perspectives |
+ | Categories | Opposing viewpoints, Legal rebuttals, Alternative interpretations, Strategic perspectives |
```

---

### Issue 9: Scope Says "DocHub (5 Templates)"

**Location:** Line 400
**Severity:** Medium

```diff
- - DocHub (5 templates with AI generation)
+ - DocHub (3 templates with AI generation: Legal Notice, Rental Agreement, Affidavit)
```

---

### Issue 10: Rate Limiting Listed as Out of Scope

**Location:** Line 415
**Severity:** High — Rate limiting is now IN scope.

```diff
- - API rate limiting / usage quotas
(Remove this line from "Out of Scope" section)
```

**Add to In Scope (line ~406):**
```diff
+ - API rate limiting (slowapi)
```

---

### Issue 11: No Upload Page Count Limit

**Location:** Section 5.5, around line 194
**Severity:** Medium

**Add row to Upload & Chat requirements table:**
```diff
  | Max File Size | 10 MB per file |
+ | Max Page Count | 300 pages per document (PDF) |
```

**Add to Acceptance Criteria:**
```diff
+ - Files exceeding 300 pages are rejected with a clear error message.
```

---

### Issue 12: No Legal Corpus Strategy

**Location:** Section 5.4 (Know Your Kanoon), AI Behavior section, around line 175
**Severity:** High — This is a foundational design decision.

**Add new sub-section after line 177:**
```diff
+ **Legal Corpus Strategy:**
+ - Curated corpus embedded in ChromaDB (not scraped, not from third-party APIs)
+ - Corpus includes: Constitution of India, Bharatiya Nyaya Sanhita (BNS), Bharatiya Nagarik Suraksha Sanhita (BNSS), Bharatiya Sakshya Adhiniyam (BSA), selected important Central Acts, selected landmark Supreme Court judgments
+ - One-time seed script processes corpus files → chunks → embeds → stores in ChromaDB
+ - No runtime web scraping or external API calls for legal data
```

---

### Issue 13: Future Roadmap Should Include Deferred Items

**Location:** Section 14, line 457
**Severity:** Low

```diff
- | **Phase 2** | Hindi language support, payment integration (Razorpay), PostgreSQL migration |
+ | **Phase 2** | NDA and Power of Attorney templates, Hindi language support, payment integration (Razorpay), PostgreSQL migration |
```

---

### Issue 14: Success Criteria References "9 Features"

**Location:** Line 443
**Severity:** Low

The count of "9 features" is still accurate (Landing, Auth, Dashboard, Know Your Kanoon, Upload & Chat, DocHub, Counter Args, Profile, Chat History). No change needed, but verify post-corrections that the feature count is still consistent.

---

## New Sections to Add

### Section 5.10: Legal Corpus (New)

Add as a new subsection in Feature Requirements:

```markdown
### 5.10 Legal Corpus

**Priority:** P0 (Must Have — required for Know Your Kanoon and Counter Arguments)

| Requirement | Details |
|-------------|---------|
| Corpus Content | Constitution of India, BNS, BNSS, BSA, selected Central Acts, selected landmark judgments |
| Source Format | Curated PDF and TXT files maintained in a seed data directory |
| Ingestion | One-time seed script: load → chunk → embed → store in ChromaDB `legal_corpus` collection |
| No External Dependencies | No scraping, no third-party legal APIs, no live web retrieval |
| Maintenance | Manual updates when new laws are added (post-MVP) |

**Acceptance Criteria:**
- Legal corpus is successfully embedded in ChromaDB on first setup.
- Know Your Kanoon queries return relevant results from the corpus.
- Corpus data is read-only after initial seeding.
```

---

## Final Recommendations

1. **Apply all 13 corrections** to PRD.md before proceeding to implementation.
2. **Add Section 5.10 (Legal Corpus)** — this is a critical missing requirement.
3. **Verify consistency** with ARCHITECTURE.md, DATABASE_SCHEMA.md, ROUTES.md, and API_SPEC.md after applying changes.
4. **Update version** to 1.1 after applying revisions.

---

> These revisions have been identified but **not yet applied** to the original PRD.md. Apply them before beginning Sprint 1 implementation.
