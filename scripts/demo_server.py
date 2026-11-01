"""Demo server for the legal agentic RAG — serves a single-page UI + API.

Modes (each labelled honestly in the UI):
  single_shot : raw case text -> BM25 legs, evidence only (no LLM)
  agent_synth : raw text -> retrieve -> LLM dossier + citation validation
                (the configuration our ablations recommend)
  agent_full  : LLM route -> retrieve -> reflect -> synthesise -> validate
                (the full agentic loop from the thesis)

NYAAY-compat: additionally exposes the API contract the adapted NYAAY-AI
frontend (demo_app/) consumes — /api/reasoning/generate plus conversation
CRUD at /api/chat/conversations, persisted to data/demo_conversations.json.

Run:  python scripts/demo_server.py          # http://127.0.0.1:8090
Deps: fastapi + uvicorn (already in venv), .env keys for LLM modes.
"""

import json
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    from dotenv import load_dotenv
    load_dotenv(project_root / ".env")
except ImportError:
    pass

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from legal_rag.chunking import RecursiveChunker
from legal_rag.datasets import load_il_pcsr
from legal_rag.legal_agent import LegalAgent
from legal_rag.llm import LLMProvider
from legal_rag.retrievers import BM25Retriever

TASKS = ("statute", "precedent")
TOP_K = 8

app = FastAPI(title="NYAAY-legal-rag demo")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # local demo — the browser preview proxy can use
                          # any port as its origin
    allow_methods=["*"],
    allow_headers=["*"],
)

STORE_PATH = project_root / "data" / "demo_conversations.json"

_state: dict = {}


def _build():
    """Load dev data + build/cached BM25 legs (chunk cache -> seconds)."""
    import hashlib
    import pickle

    data_root = project_root / "data" / "raw" / "il_pcsr"
    cache_dir = project_root / "data" / "cache"
    chunker = RecursiveChunker(size=512, overlap=50)
    retrievers, doc_texts, doc_titles, queries = {}, {}, {}, {}
    for task in TASKS:
        qs, docs = load_il_pcsr(data_root, "dev", task)
        queries[task] = qs
        doc_texts[task] = {d.doc_id: d.raw_text for d in docs}
        doc_titles[task] = {d.doc_id: d.title for d in docs}
        h = hashlib.sha256()
        for d in docs:
            h.update(d.raw_text.encode())
        cp = cache_dir / f"chunks_{task}_dev_{h.hexdigest()[:16]}.pkl"
        if cp.exists():
            chunks = pickle.loads(cp.read_bytes())
        else:
            chunks = chunker.chunk(docs)
            cp.write_bytes(pickle.dumps(chunks))
        r = BM25Retriever(ngram=2, cache_dir=cache_dir)
        r.index(chunks)
        retrievers[task] = r
        print(f"[init] {task}: {len(docs)} docs indexed", flush=True)
    _state.update(retrievers=retrievers, doc_texts=doc_texts,
                  doc_titles=doc_titles, queries=queries,
                  llm=LLMProvider())
    print(f"[init] llm: {_state['llm'].provider}/{_state['llm'].model}",
          flush=True)


class AnalyzeReq(BaseModel):
    case_text: str
    mode: str = "agent_synth"          # single_shot | agent_synth | agent_full
    tasks: list[str] = list(TASKS)


def _evidence_payload(evidence: dict) -> dict:
    out = {}
    for task, hits in evidence.items():
        if isinstance(hits, dict):
            hits = sorted(hits.items(), key=lambda kv: kv[1], reverse=True)
        out[task] = [
            {"id": did, "score": round(float(s), 3),
             "title": _state["doc_titles"][task].get(did, "")[:120],
             "snippet": _state["doc_texts"][task].get(did, "")[:300]}
            for did, s in hits[:TOP_K]
        ]
    return out


def _trace_payload(trace) -> list:
    return [
        {"step": s.step,
         "latency_s": round(s.latency_seconds, 2),
         "detail": {k: v for k, v in s.detail.items()
                    if k in ("queries", "counts", "sufficient", "round")}}
        for s in trace
    ]


@app.post("/api/analyze")
def analyze(req: AnalyzeReq):
    t_start = time.perf_counter()
    tasks = [t for t in req.tasks if t in TASKS] or list(TASKS)
    agent = LegalAgent(
        {t: _state["retrievers"][t] for t in tasks},
        {t: _state["doc_texts"][t] for t in tasks},
        _state["llm"],
        {t: _state["doc_titles"][t] for t in tasks},
        max_extra_rounds=1, top_k=TOP_K,
    )
    mode = req.mode
    if mode == "single_shot":
        evidence = {
            t: dict(_state["retrievers"][t].search(req.case_text, top_k=TOP_K))
            for t in tasks
        }
        dossier, warnings, trace = {}, [], []
    elif mode == "agent_full":
        res = agent.run(req.case_text)
        evidence = {t: dict(res.evidence.get(t, [])) for t in tasks}
        dossier, warnings, trace = res.dossier, res.warnings, res.trace
    else:  # agent_synth: raw-text retrieval + LLM synthesis (recommended cfg)
        from legal_rag.legal_agent import AgentStep
        evidence = {}
        t0 = time.perf_counter()
        queries = {t: req.case_text for t in tasks}
        agent._retrieve(queries, evidence)
        trace = [AgentStep("retrieve", {"queries": {
                    t: "<raw case text>" for t in tasks},
                    "counts": {t: len(e) for t, e in evidence.items()}},
                 time.perf_counter() - t0)]
        t0 = time.perf_counter()
        dossier = agent._synthesize(req.case_text, evidence)
        dropped = agent._validate_citations(dossier, evidence)
        warnings = ([f"dropped unverifiable citations: {dropped}"]
                    if dropped else [])
        trace.append(AgentStep("synthesize", {"dossier": dossier},
                               time.perf_counter() - t0))

    return {
        "mode": mode,
        "tasks": tasks,
        "legs": {"statute": "BM25 2-gram", "precedent": "BM25 2-gram"},
        "evidence": _evidence_payload(evidence),
        "dossier": dossier,
        "warnings": warnings,
        "trace": _trace_payload(trace),
        "wall_s": round(time.perf_counter() - t_start, 2),
        "llm": f"{_state['llm'].provider}/{_state['llm'].model}",
    }


@app.get("/api/sample")
def sample(task: str = "statute", idx: int = 0):
    qs = _state["queries"].get(task) or _state["queries"]["statute"]
    q = qs[idx % len(qs)]
    return {"qid": q.qid, "task": task, "text": q.text,
            "ground_truth": q.ground_truth}


@app.get("/api/samples")
def samples():
    out = {}
    for task in TASKS:
        out[task] = [{"qid": q.qid, "n": i} for i, q in
                     enumerate(_state["queries"][task][:20])]
    return out


@app.get("/", response_class=HTMLResponse)
def index():
    return (project_root / "demo_ui" / "index.html").read_text()


# ---------------------------------------------------------------------------
# NYAAY-AI-compatible API (consumed by demo_app/, the adapted NYAAY frontend)
# ---------------------------------------------------------------------------

def _load_store() -> list:
    if STORE_PATH.exists():
        try:
            return json.loads(STORE_PATH.read_text())
        except Exception:
            pass
    return []


def _save_store(convs: list):
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STORE_PATH.write_text(json.dumps(convs, indent=1))


def _find_conv(cid: str) -> dict:
    conv = next((c for c in _load_store() if c["id"] == cid), None)
    if conv is None:
        raise HTTPException(404, f"conversation {cid} not found")
    return conv


def _conv_summary(c: dict) -> dict:
    return {k: c[k] for k in
            ("id", "title", "is_pinned", "feature_type", "created_at",
             "updated_at")}


def _synth_pipeline(case_text: str, tasks: tuple = TASKS):
    """Raw-text retrieval + LLM synthesis — the config our ablations
    recommend (agent_synth). Returns (evidence, dossier, warnings, trace)."""
    from legal_rag.legal_agent import AgentStep
    agent = LegalAgent(
        {t: _state["retrievers"][t] for t in tasks},
        {t: _state["doc_texts"][t] for t in tasks},
        _state["llm"],
        {t: _state["doc_titles"][t] for t in tasks},
        max_extra_rounds=1, top_k=TOP_K,
    )
    evidence: dict = {}
    t0 = time.perf_counter()
    agent._retrieve({t: case_text for t in tasks}, evidence)
    trace = [AgentStep("retrieve",
                       {"queries": {t: "<raw case text>" for t in tasks},
                        "counts": {t: len(e) for t, e in evidence.items()}},
                       time.perf_counter() - t0)]
    t0 = time.perf_counter()
    dossier = agent._synthesize(case_text, evidence)
    dropped = agent._validate_citations(dossier, evidence)
    warnings = ([f"dropped unverifiable citations: {dropped}"]
                if dropped else [])
    trace.append(AgentStep("synthesize", {"dossier": dossier},
                           time.perf_counter() - t0))
    return evidence, dossier, warnings, trace


_STOPWORDS = {"that", "with", "this", "from", "have", "been", "what",
              "were", "they", "their", "which", "when", "will", "shall",
              "into", "under", "over", "case", "about", "there", "then",
              "than", "them", "also", "such", "only", "some", "other"}


def _relevant_excerpt(text: str, query: str, max_sents: int = 2,
                      width: int = 420) -> str:
    """Pick the sentences of *text* sharing the most content terms with
    *query* — a cheap stand-in for true passage highlighting."""
    import re
    sents = re.split(r"(?<=[.!?;])\s+", " ".join(text.split()))
    qterms = {w.lower() for w in re.findall(r"[A-Za-z]{4,}", query)}
    qterms -= _STOPWORDS
    if not qterms or not sents:
        return " ".join(text.split())[:width]
    scored = sorted(
        sents,
        key=lambda s: len(qterms & {w.lower()
                                    for w in re.findall(r"[A-Za-z]{4,}", s)}),
        reverse=True,
    )
    top = [s for s in scored[:max_sents]]
    # restore document order for readability
    top = [s for s in sents if s in top]
    return " … ".join(top)[:width]


def _web_fallback(query_text: str, n: int = 5) -> tuple[list, str | None]:
    """External supplementary retrieval via the OpenAI-compatible
    Responses API with the ``web_search_preview`` tool. Returns
    (sources, context_text): sources are the emitted URL citations,
    context_text is the model's web-grounded answer. Falls back to a
    keyless Wikipedia search when the API call fails."""
    import os
    import urllib.parse
    import urllib.request

    key = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
    base = (os.getenv("LLM_BASE_URL")
            or "https://api.openai.com/v1").rstrip("/")
    model = getattr(_state.get("llm"), "model", None) \
        or os.getenv("LLM_MODEL", "gpt-6-luna")
    if key:
        payload = {
            "model": model,
            "input": (
                "Using authoritative public sources (legislation, "
                "regulators, courts, official commentary), briefly answer "
                "this legal question and cite your sources: "
                + " ".join(query_text.split()[:120])),
            "tools": [{"type": "web_search_preview"}],
        }
        try:
            req = urllib.request.Request(
                f"{base}/responses",
                data=json.dumps(payload).encode(),
                headers={"Authorization": f"Bearer {key}",
                         "Content-Type": "application/json"})
            data = json.loads(
                urllib.request.urlopen(req, timeout=90).read())
            text, sources = "", []
            for item in data.get("output", []):
                if item.get("type") != "message":
                    continue
                for c in item.get("content", []):
                    if c.get("type") == "output_text":
                        text = c.get("text", "")
                        for a in c.get("annotations", []):
                            if a.get("type") == "url_citation":
                                u = a.get("url", "")
                                sources.append({
                                    "title": a.get("title") or u,
                                    "excerpt": urllib.parse.urlparse(u)
                                    .netloc.replace("www.", ""),
                                    "url": u})
            seen, uniq = set(), []
            for s in sources:
                if s["url"] not in seen:
                    seen.add(s["url"])
                    uniq.append(s)
            if text or uniq:
                return uniq[:n], text.strip() or None
        except Exception as exc:  # noqa: BLE001
            print(f"[web_fallback] responses api failed: {exc}",
                  flush=True)

    # Keyless backup: Wikipedia REST search (AND-matched; coarse).
    import re as _re
    q = urllib.parse.quote(" ".join(query_text.split()[:30]))
    url = ("https://en.wikipedia.org/w/rest.php/v1/search/page"
           f"?q={q}&limit={n}")
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "legal-rag-demo/1.0"})
        data = json.loads(urllib.request.urlopen(req, timeout=10).read())
    except Exception as exc:  # noqa: BLE001
        print(f"[web_fallback] wikipedia failed: {exc}", flush=True)
        return [], None
    out = [{
        "title": p.get("title", ""),
        "excerpt": _re.sub(r"<[^>]+>", "", p.get("excerpt", ""))[:300],
        "url": "https://en.wikipedia.org/wiki/"
               + p.get("key", p.get("title", "").replace(" ", "_")),
    } for p in data.get("pages", [])[:n]]
    return out, None


def _nyaay_content(dossier: dict, evidence: dict, case_text: str,
                   external: list | None = None,
                   supplementary: str | None = None) -> str:
    """Adapt our compact dossier to the rich section schema that
    NYAAY's LegalAnalysisRenderer expects."""
    statutes = [
        {"section": s.get("id", ""),
         "act": _state["doc_titles"]["statute"].get(s.get("id", ""), "")[:90]
               or "IL-PCSR statute",
         "relevance": s.get("relevance", "")}
        for s in dossier.get("applicable_statutes", [])
    ]
    precedents = [
        {"case_name":
            _state["doc_titles"]["precedent"].get(p.get("id", ""), "")[:110]
            or p.get("id", ""),
         "citation": p.get("id", ""),
         "holding": p.get("relevance", "")}
        for p in dossier.get("supporting_precedents", [])
    ]
    n_s = len(evidence.get("statute", {}))
    n_p = len(evidence.get("precedent", {}))
    issue = dossier.get("issue", "")

    retrieved_sources = []
    for task in TASKS:
        hits = evidence.get(task, {})
        if isinstance(hits, dict):
            hits = sorted(hits.items(), key=lambda kv: kv[1],
                          reverse=True)
        for did, score in list(hits)[:3]:
            title = _state["doc_titles"][task].get(did, "")
            retrieved_sources.append({
                "id": did,
                "corpus": task,
                "bm25_score": f"{float(score):.2f}",
                "title": title[:100] or did,
                "excerpt": _relevant_excerpt(
                    _state["doc_texts"][task].get(did, ""), case_text),
            })

    grounding = (
        f"Grounded on {n_s} retrieved statutes and {n_p} retrieved "
        f"precedents from the IL-PCSR corpus; every citation above was "
        "validated against the retrieved document set."
    )
    if external:
        grounding += (" Corpus evidence was weak — see the external "
                      "references below, which are NOT corpus-grounded.")

    # The first card is THE ANSWER: framed issue + corpus-grounded
    # analysis; external context appended when the web fallback fired.
    answer = f"**Issue.** {issue}\n\n{dossier.get('analysis', '')}"
    if supplementary:
        answer += ("\n\n**External context (not corpus-grounded).** "
                   + supplementary)

    doc = {
        "executive_summary": answer,
        "applicable_statutes": statutes,
        "judicial_precedents": precedents,
        "retrieved_sources": retrieved_sources,
        "confidence_summary": grounding,
        "external_sources": external or [],
        "supplementary_context": supplementary or "",
    }
    return json.dumps({k: v for k, v in doc.items() if v not in ([], "")})


def _citations_payload(dossier: dict) -> list:
    out = []
    for s in dossier.get("applicable_statutes", []):
        out.append({"act": _state["doc_titles"]["statute"]
                            .get(s.get("id", ""), "")[:80] or "Statute",
                    "section": s.get("id", ""),
                    "excerpt": s.get("relevance", "")})
    for p in dossier.get("supporting_precedents", []):
        out.append({"act": _state["doc_titles"]["precedent"]
                            .get(p.get("id", ""), "")[:80] or "Precedent",
                    "section": p.get("id", ""),
                    "excerpt": p.get("relevance", "")})
    return out


class ReasoningReq(BaseModel):
    user_facts: str
    tenant_id: str = "global"
    language: str = "en"
    detected_lang: str | None = None
    conversation_id: str | None = None


@app.post("/api/reasoning/generate")
def reasoning_generate(req: ReasoningReq):
    now = datetime.now(timezone.utc).isoformat()
    convs = _load_store()
    conv = next((c for c in convs
                 if c["id"] == req.conversation_id), None)
    if conv is None:
        conv = {
            "id": str(uuid.uuid4()),
            "title": req.user_facts[:80],
            "is_pinned": False,
            "feature_type": "legal_reasoning",
            "created_at": now,
            "updated_at": now,
            "messages": [],
        }
        convs.append(conv)

    evidence, dossier, warnings, trace = _synth_pipeline(req.user_facts)
    citations = _citations_payload(dossier)

    # Weak-evidence gate: no validated citations, or the strongest BM25
    # hit is noise-level -> fetch external public references.
    top_score = 0.0
    for hits in evidence.values():
        seq = hits.items() if isinstance(hits, dict) else hits
        for _did, s in seq:
            top_score = max(top_score, float(s))
    external, supplementary = [], None
    if not citations or top_score < 8.0:
        external, supplementary = _web_fallback(req.user_facts)
        if external or supplementary:
            warnings = list(warnings) + [
                f"low corpus evidence (citations={len(citations)}, "
                f"top_score={top_score:.1f}) — {len(external)} external "
                "references fetched via web search; NOT corpus-grounded"]
            from legal_rag.legal_agent import AgentStep
            trace.append(AgentStep(
                "web_fallback",
                {"reason": "weak corpus evidence",
                 "sources": len(external)}, 0.0))

    content = _nyaay_content(dossier, evidence, req.user_facts,
                             external, supplementary)
    analysis_id = str(uuid.uuid4())

    conv["messages"].append({"role": "user", "content": req.user_facts,
                             "created_at": now})
    conv["messages"].append({"role": "assistant", "content": content,
                             "citations": citations, "id": analysis_id,
                             "created_at": now})
    conv["updated_at"] = now
    _save_store(convs)

    return {
        "content": content,
        "citations": citations,
        "analysis_id": analysis_id,
        "conversation_id": conv["id"],
        "sources": _evidence_payload(evidence),
        "warnings": warnings,
    }


@app.get("/api/chat/conversations")
def chat_conversations(feature_type: str | None = None, query: str | None = None):
    convs = [c for c in _load_store()
             if feature_type is None or c.get("feature_type") == feature_type]
    if query:
        q = query.lower()
        convs = [c for c in convs if q in c.get("title", "").lower()]
    convs.sort(key=lambda c: c.get("updated_at", ""), reverse=True)
    return {"conversations": [_conv_summary(c) for c in convs]}


@app.get("/api/chat/conversations/{cid}/messages")
def chat_messages(cid: str):
    conv = _find_conv(cid)
    return {"messages": conv.get("messages", [])}


class RenameReq(BaseModel):
    title: str


class PinReq(BaseModel):
    is_pinned: bool


@app.put("/api/chat/conversations/{cid}/rename")
def chat_rename(cid: str, req: RenameReq):
    convs = _load_store()
    conv = next((c for c in convs if c["id"] == cid), None)
    if conv is None:
        raise HTTPException(404, f"conversation {cid} not found")
    conv["title"] = req.title
    conv["updated_at"] = datetime.now(timezone.utc).isoformat()
    _save_store(convs)
    return _conv_summary(conv)


@app.put("/api/chat/conversations/{cid}/pin")
def chat_pin(cid: str, req: PinReq):
    convs = _load_store()
    conv = next((c for c in convs if c["id"] == cid), None)
    if conv is None:
        raise HTTPException(404, f"conversation {cid} not found")
    conv["is_pinned"] = req.is_pinned
    _save_store(convs)
    return _conv_summary(conv)


@app.delete("/api/chat/conversations/{cid}")
def chat_delete(cid: str):
    convs = _load_store()
    convs = [c for c in convs if c["id"] != cid]
    _save_store(convs)
    return {"deleted": True}


if __name__ == "__main__":
    _build()
    uvicorn.run(app, host="127.0.0.1", port=8090, log_level="warning")
