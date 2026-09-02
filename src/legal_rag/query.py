import time
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class QueryTransformation:
    original: str
    transformed: str
    strategy: str
    hypothetical_document: str | None = None
    latency_seconds: float = 0.0
    token_usage: dict[str, int] | None = None
    cost_usd: float | None = None


class QueryStrategy(ABC):
    @abstractmethod
    def transform(self, query: str) -> QueryTransformation:
        ...


class DirectQueryStrategy(QueryStrategy):
    def transform(self, query: str) -> QueryTransformation:
        return QueryTransformation(
            original=query,
            transformed=query,
            strategy="direct",
            latency_seconds=0.0,
        )


class KeywordExpansionQueryStrategy(QueryStrategy):
    _expansions: dict[str, list[str]] = {
        "dishonestly": ["fraudulently"],
        "induces": ["causes", "compels"],
        "delivery": ["transfer"],
        "entrusted": ["confided"],
        "misappropriates": ["embezzles"],
    }

    def transform(self, query: str) -> QueryTransformation:
        start = time.perf_counter()
        words = query.lower().split()
        expanded: list[str] = []
        for w in words:
            expanded.append(w)
            clean = w.strip(".,;:")
            if clean in self._expansions:
                expanded.extend(self._expansions[clean])
        transformed = " ".join(expanded)
        latency = time.perf_counter() - start
        return QueryTransformation(
            original=query,
            transformed=transformed,
            strategy="keyword_expansion",
            latency_seconds=latency,
        )


class HyDEQueryStrategy(QueryStrategy):
    def transform(self, query: str) -> QueryTransformation:
        start = time.perf_counter()
        hypothetical = (
            f"A relevant legal document for the situation \"{query}\" "
            "would describe the applicable statutory provision, the material facts, and the court's reasoning."
        )
        transformed = f"{query} {hypothetical}"
        latency = time.perf_counter() - start
        return QueryTransformation(
            original=query,
            transformed=transformed,
            strategy="hyde",
            hypothetical_document=hypothetical,
            latency_seconds=latency,
        )
