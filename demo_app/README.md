# NYAAY-AI adapted frontend (dissertation demo)

A trimmed adaptation of the NYAAY-AI React frontend, wired to this
repository's legal-RAG agent instead of the original backend.

What was kept: the full paper-toned design system (Tailwind theme, serif
typography, `Ny` branding), the `LegalReasoning` chat surface
(sidebar conversation history, pin/rename/delete, message bubbles,
`LegalAnalysisRenderer` dossier cards), i18n scaffolding, and the
conversation CRUD service contracts.

What was removed: Firebase auth (`AuthContext` is a stub), protected
routes, and all NYAAY product modules other than Reasoning (Dashboard,
Civic Navigator, Kanoon Q&A, Doc Chat, Drafting).

What was added: `?conv=<id>` deep-linking to a saved conversation.

Backend contract (implemented in `scripts/demo_server.py`):
  GET    /api/chat/conversations?feature_type=legal_reasoning
  GET    /api/chat/conversations/{id}/messages
  PUT    /api/chat/conversations/{id}/rename   {title}
  PUT    /api/chat/conversations/{id}/pin      {is_pinned}
  DELETE /api/chat/conversations/{id}
  POST   /api/reasoning/generate   {user_facts, conversation_id?}

Run:
  python scripts/demo_server.py          # backend on :8090
  cd demo_app && npm install && npm run dev   # frontend on :3000
