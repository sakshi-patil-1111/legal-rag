# NYAAY AI Drafting Engine — Architecture

**Version**: 1.0.0
**Status**: Production Ready (v1.0)
**Validated against acceptance suite on**: 30 June 2026

## Core Design Principles
1. **LLM generates facts, never formatting**: The AI focuses exclusively on generating legally accurate text and extracting user intents.
2. **Formatting is deterministic**: Visual layout, margins, and placement are strictly controlled by the DocumentGenerator code, never by the LLM.
3. **Templates own presentation**: The individual templates (e.g. `affidavit`, `police_complaint`) dictate the required fields, specific legal headers, and precise layouts.
4. **StructuredDocumentObject is the single source of truth**: Every downstream process relies on this JSON object.
5. **PDF, DOCX and Preview must remain identical**: The outputs must be perfectly parallel representations of the structured object.
6. **Prompt changes must never break API contracts**: Modifying template instructions must not alter the expected JSON outputs.
7. **Every document must be reproducible**: Passing the exact same `StructuredDocumentObject` into the generator must yield the exact same PDF.

## Document Lifecycle
The engine enforces a strictly linear progression that prohibits the LLM from hallucinating formatting at later stages:
```
User Facts
    ↓
StructuredDocumentObject
    ↓
Preview (UI)
    ↓
PDF Generation
    ↓
DOCX Generation
    ↓
Print
    ↓
Archive
```
> **Architectural Guarantee**: Every output originates directly from the `StructuredDocumentObject`. Output is *never* generated from raw, regenerated LLM markdown text.

## Architecture Diagram
```mermaid
flowchart TD
    A[Client UI] -->|POST /generate| B[DraftingOrchestrator]
    B -->|Classify Intent| C{Doc Type Identified?}
    C -->|No| D[Ask for Clarification]
    C -->|Yes| E[Load Template Schema & Instructions]
    
    E --> F[Missing Info Wizard]
    F -->|Fields Missing| G[Return MISSING_INFO Status]
    G --> A
    
    F -->|Fields Provided| H[Gemini LLM JSON Generation]
    H --> I[Pydantic model_validate_json]
    I -->|Error| J[Automatic Retry Loop]
    J --> H
    I -->|Success| K[StructuredDocumentObject]
    
    K --> L[DocumentGenerator (PDF/DOCX)]
    L --> M[Return SUCCESS Status]
    M --> A
```

## Public API Specification

### `POST /api/drafting/generate`
- **Payload**: `{"user_facts": str, "provided_fields": Optional[Dict[str, str]]}`
- **Behavior**: Classifies intent, identifies missing mandatory fields. If fields are missing, returns `MISSING_INFO`. Otherwise, attempts to generate the V1 Draft.
- **Returns**: `{"status": "SUCCESS" | "MISSING_INFO" | "UNKNOWN", "document_object": Optional[Dict], "missing_fields": Optional[List]}`

### `POST /api/drafting/edit`
- **Payload**: `{"document_object": Dict, "edit_instructions": str}`
- **Behavior**: Instructs the LLM to selectively rewrite targeted paragraphs. Increments `metadata.version`.
- **Returns**: `StructuredDocumentObject`

## Versioning Policy
To ensure maintainability, all changes to the Drafting Engine must strictly follow Semantic Versioning (SemVer):

- **MAJOR (e.g. v2.0.0)**: Breaking API changes, or structural changes to the `StructuredDocumentObject` schema that break backward compatibility.
- **MINOR (e.g. v1.1.0)**: Adding new document templates to the registry, adding new export formats (e.g., HTML), or introducing optional non-breaking schema fields.
- **PATCH (e.g. v1.0.1)**: Bug fixes, performance improvements, prompt refinements in `instructions.md`, or fixes to PDF margin bugs.

## Breaking Change Policy (The "Freeze" Rules)
Any architectural modification to the `DraftingOrchestrator` requires:
- Architecture Review
- Regression Suite Pass
- Version Increment
- Updated Production Readiness Report

## Future Extensions
Future additions to the drafting engine should focus entirely on expanding the Template Registry, rather than rewriting the core architecture. Supported extension points include adding folders for:
- Court Petitions
- Bail Applications
- Written Statements
- Plaints
- Writ Petitions
- Appeals
- Contracts
- Employment Agreements
- Rental Agreements
- Wills
- Gift Deeds

## Observability Metrics
While not fully collected today, the architecture must support the future tracking of the following observability metrics:
- Generation Success %
- Retry Rate
- JSON Validation Failures
- Average Generation Time
- Average Edit Time
- PDF Generation Time
- DOCX Generation Time
- Most Used Template
