"""Agentic RAG orchestrator for legal case analysis.

Pipeline: route -> retrieve -> reflect (bounded) -> grounded dossier.

The agent treats per-task retrievers as tools. An LLM decides which
corpora to query, optionally refines queries after inspecting evidence,
and produces a structured dossier whose citations are validated against
the retrieved document set.
"""

import json
import re
import time
from dataclasses import dataclass, field
from typing import Any

from .llm import LLMProvider
from .retrievers.base import Retriever

ROUTE_SYSTEM = (
    "You are the routing component of a legal case-analysis agent. "
    "Given a case description, decide which corpora to search and write a "
    "short focused search query for each needed corpus. Corpora: 'statute' "
    "(Indian statutes/provisions) and 'precedent' (prior case judgments). "
    "Respond with JSON only: "
    '{"statute": "<query or null>", "precedent": "<query or null>"}.'
)

REFLECT_SYSTEM = (
    "You are the reflection component of a legal case-analysis agent. "
    "Given a case description and the candidates retrieved so far, decide "
    "whether the evidence is sufficient to answer. If not, provide refined "
    "search queries. Respond with JSON only: "
    '{"sufficient": true|false, "statute": "<query or null>", '
    '"precedent": "<query or null>"}.'
)

SYNTH_SYSTEM = (
    "You are the synthesis component of a legal case-analysis agent. "
    "Using ONLY the provided retrieved documents, produce a JSON dossier: "
    '{"issue": "...", "applicable_statutes": [{"id": "...", "relevance": "..."}], '
    '"supporting_precedents": [{"id": "...", "relevance": "..."}], '
    '"analysis": "...", "suggested_action": "..."}. '
    "Only cite document IDs that appear in the provided evidence list. "
    "If evidence is weak, say so inside 'analysis' instead of inventing sources."
)


def _extract_json(text: str) -> dict[str, Any] | None:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


@dataclass
class AgentStep:
    step: str
    detail: dict[str, Any]
    latency_seconds: float


@dataclass
class AgentResult:
    dossier: dict[str, Any]
    evidence: dict[str, list[tuple[str, float]]]
    trace: list[AgentStep] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class LegalAgent:
    """Route -> retrieve -> reflect -> synthesize loop over task retrievers."""

    def __init__(
        self,
        retrievers: dict[str, Retriever],
        doc_texts: dict[str, dict[str, str]],
        llm: LLMProvider,
        doc_titles: dict[str, dict[str, str]] | None = None,
        max_extra_rounds: int = 1,
        top_k: int = 8,
        snippet_chars: int = 1500,
    ):
        self.retrievers = retrievers
        self.doc_texts = doc_texts
        self.doc_titles = doc_titles or {t: {} for t in retrievers}
        self.llm = llm
        self.max_extra_rounds = max_extra_rounds
        self.top_k = top_k
        self.snippet_chars = snippet_chars

    def _route(self, case_text: str) -> dict[str, str]:
        try:
            resp = self.llm.generate(
                f"Case description:\n{case_text[:6000]}", system=ROUTE_SYSTEM,
                temperature=0.0, max_tokens=300,
            )
        except Exception:
            return {task: case_text[:2000] for task in self.retrievers}
        plan = _extract_json(resp.text) or {}
        queries = {}
        for task in self.retrievers:
            q = plan.get(task)
            if isinstance(q, str) and q.strip():
                queries[task] = q.strip()
        if not queries:
            queries = {task: case_text[:2000] for task in self.retrievers}
        return queries

    def _retrieve(
        self, queries: dict[str, str], evidence: dict[str, dict[str, float]],
    ) -> None:
        for task, q in queries.items():
            retriever = self.retrievers.get(task)
            if retriever is None:
                continue
            hits = retriever.search(q, top_k=self.top_k)
            task_ev = evidence.setdefault(task, {})
            for doc_id, score in hits:
                if doc_id not in task_ev or score > task_ev[doc_id]:
                    task_ev[doc_id] = score

    def _reflect(
        self, case_text: str, evidence: dict[str, dict[str, float]],
    ) -> dict[str, str] | None:
        summary_parts = []
        for task, ev in evidence.items():
            titles = self.doc_titles.get(task, {})
            lines = ", ".join(
                f"{doc_id} ({titles.get(doc_id, '')[:60]})"
                for doc_id in sorted(ev, key=ev.get, reverse=True)[:10]
            )
            summary_parts.append(f"{task}: {lines}")
        prompt = (
            f"Case description:\n{case_text[:4000]}\n\n"
            f"Retrieved candidates:\n" + "\n".join(summary_parts)
        )
        try:
            resp = self.llm.generate(prompt, system=REFLECT_SYSTEM, temperature=0.0, max_tokens=300)
        except Exception:
            return None
        verdict = _extract_json(resp.text) or {}
        if verdict.get("sufficient"):
            return None
        refined = {}
        for task in self.retrievers:
            q = verdict.get(task)
            if isinstance(q, str) and q.strip():
                refined[task] = q.strip()
        return refined or None

    def _synthesize(
        self, case_text: str, evidence: dict[str, dict[str, float]],
    ) -> dict[str, Any]:
        blocks = []
        for task, ev in evidence.items():
            texts = self.doc_texts.get(task, {})
            titles = self.doc_titles.get(task, {})
            top = sorted(ev, key=ev.get, reverse=True)[: self.top_k]
            for doc_id in top:
                snippet = texts.get(doc_id, "")[: self.snippet_chars]
                blocks.append(
                    f"[{task}] {doc_id} | {titles.get(doc_id, '')}\n{snippet}"
                )
        prompt = (
            f"Case description:\n{case_text[:4000]}\n\n"
            f"Retrieved evidence ({sum(len(v) for v in evidence.values())} docs):\n\n"
            + "\n\n".join(blocks)
        )
        try:
            resp = self.llm.generate(prompt, system=SYNTH_SYSTEM, temperature=0.2, max_tokens=1500)
        except Exception as exc:
            return {"issue": "", "analysis": f"LLM synthesis unavailable: {exc}",
                    "suggested_action": "", "applicable_statutes": [],
                    "supporting_precedents": []}
        dossier = _extract_json(resp.text)
        if dossier is None:
            return {"issue": "", "analysis": resp.text, "suggested_action": "",
                    "applicable_statutes": [], "supporting_precedents": []}
        return dossier

    def _validate_citations(
        self, dossier: dict[str, Any], evidence: dict[str, dict[str, float]],
    ) -> list[str]:
        valid_ids = {i for ev in evidence.values() for i in ev}
        dropped = []
        for key in ("applicable_statutes", "supporting_precedents"):
            items = dossier.get(key)
            if not isinstance(items, list):
                dossier[key] = []
                continue
            kept = [c for c in items if c.get("id") in valid_ids]
            dropped.extend(c.get("id", "?") for c in items if c.get("id") not in valid_ids)
            dossier[key] = kept
        return dropped

    def run(self, case_text: str) -> AgentResult:
        trace: list[AgentStep] = []
        warnings: list[str] = []

        t0 = time.perf_counter()
        queries = self._route(case_text)
        trace.append(AgentStep("route", {"queries": queries}, time.perf_counter() - t0))

        evidence: dict[str, dict[str, float]] = {}
        t0 = time.perf_counter()
        self._retrieve(queries, evidence)
        trace.append(AgentStep(
            "retrieve",
            {"queries": queries, "counts": {t: len(e) for t, e in evidence.items()}},
            time.perf_counter() - t0,
        ))

        for rnd in range(1, self.max_extra_rounds + 1):
            t0 = time.perf_counter()
            refined = self._reflect(case_text, evidence)
            trace.append(AgentStep(
                "reflect",
                {"round": rnd, "sufficient": refined is None, "refined": refined},
                time.perf_counter() - t0,
            ))
            if refined is None:
                break
            t0 = time.perf_counter()
            self._retrieve(refined, evidence)
            trace.append(AgentStep(
                "retrieve",
                {"queries": refined, "counts": {t: len(e) for t, e in evidence.items()}},
                time.perf_counter() - t0,
            ))

        t0 = time.perf_counter()
        dossier = self._synthesize(case_text, evidence)
        dropped = self._validate_citations(dossier, evidence)
        if dropped:
            warnings.append(f"dropped unverifiable citations: {dropped}")
        trace.append(AgentStep("synthesize", {"dossier": dossier}, time.perf_counter() - t0))

        flat_evidence = {
            task: sorted(ev.items(), key=lambda kv: kv[1], reverse=True)
            for task, ev in evidence.items()
        }
        return AgentResult(dossier=dossier, evidence=flat_evidence, trace=trace, warnings=warnings)
