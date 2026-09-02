import time
from dataclasses import dataclass, field
from typing import Any

from .query import DirectQueryStrategy, HyDEQueryStrategy, QueryStrategy
from .retrievers.base import Retriever


@dataclass
class AgentState:
    round_number: int
    action: str
    reason: str
    query_transformation: str
    evidence: list[tuple[str, float]]


@dataclass
class AgentTrace:
    query: str
    rounds: list[AgentState] = field(default_factory=list)
    stop_reason: str = ""
    total_latency: float = 0.0


class ConstrainedAgent:
    def __init__(
        self,
        retriever: Retriever,
        strategies: list[QueryStrategy] | None = None,
        max_rounds: int = 2,
        score_threshold: float = float("inf"),
    ):
        self.retriever = retriever
        self.strategies = strategies or [DirectQueryStrategy(), HyDEQueryStrategy()]
        self.max_rounds = max_rounds
        self.score_threshold = score_threshold

    def _texts_by_id(self, items: list[Any]) -> dict[str, str]:
        texts: dict[str, str] = {}
        for item in items:
            ext = item.parent_doc_id if hasattr(item, "parent_doc_id") else None
            if ext is None:
                ext = item.doc_id
            text = getattr(item, "text", getattr(item, "raw_text", ""))
            if ext not in texts or len(text) > len(texts[ext]):
                texts[ext] = text
        return texts

    def run(
        self,
        query: str,
        top_k: int = 10,
    ) -> tuple[list[tuple[str, float]], AgentTrace]:
        start = time.perf_counter()
        trace = AgentTrace(query=query)
        best_evidence: list[tuple[str, float]] = []

        for round_number, strategy in enumerate(self.strategies, start=1):
            t0 = time.perf_counter()
            tq = strategy.transform(query)
            evidence = self.retriever.search(tq.transformed, top_k=top_k)
            latency = time.perf_counter() - t0

            state = AgentState(
                round_number=round_number,
                action=strategy.__class__.__name__,
                reason=f"round {round_number} retrieval with {tq.strategy}",
                query_transformation=tq.transformed,
                evidence=evidence,
            )
            trace.rounds.append(state)

            if evidence:
                best_evidence = evidence
                max_score = max(score for _, score in evidence)
                if round_number >= self.max_rounds or max_score > self.score_threshold:
                    trace.stop_reason = (
                        "max_rounds_reached" if round_number >= self.max_rounds else "score_threshold_met"
                    )
                    break

        if not trace.stop_reason:
            trace.stop_reason = "max_rounds_reached"

        trace.total_latency = time.perf_counter() - start
        return best_evidence, trace
