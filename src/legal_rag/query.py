import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from .llm import LLMProvider


@dataclass
class QueryTransformation:
    original: str
    transformed: str
    strategy: str
    hypothetical_document: str | None = None
    latency_seconds: float = 0.0
    token_usage: dict[str, int] | None = None
    cost_usd: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "original": self.original,
            "transformed": self.transformed,
            "strategy": self.strategy,
            "hypothetical_document": self.hypothetical_document,
            "latency_seconds": self.latency_seconds,
            "token_usage": self.token_usage,
            "cost_usd": self.cost_usd,
        }


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
    """Static HyDE — no LLM call, just template concatenation.

    Kept for backward compatibility with tests. Use LLMHyDEStrategy
    for real LLM-generated hypothetical documents.
    """

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


class LLMQueryRewriteStrategy(QueryStrategy):
    """LLM-based query rewriting for legal retrieval.

    Asks an LLM to rewrite the query into a more retrieval-oriented form
    while preserving the legal intent.
    """

    REWRITE_SYSTEM = (
        "You are a legal search assistant. Rewrite the user's legal query "
        "into a more effective search query for a legal document retrieval system. "
        "Keep it concise, preserve key legal terms and citations, and expand "
        "abbreviations. Output ONLY the rewritten query, nothing else."
    )

    def __init__(self, **kwargs):
        self.llm = LLMProvider(**kwargs)

    def transform(self, query: str) -> QueryTransformation:
        prompt = f"Original query: {query}\n\nRewritten query:"
        resp = self.llm.generate(prompt, system=self.REWRITE_SYSTEM, temperature=0.2, max_tokens=256)
        rewritten = resp.text.strip()
        return QueryTransformation(
            original=query,
            transformed=rewritten,
            strategy="llm_rewrite",
            latency_seconds=resp.latency_seconds,
            token_usage={"in": resp.tokens_in, "out": resp.tokens_out},
            cost_usd=resp.cost_usd,
        )


class LLMHyDEStrategy(QueryStrategy):
    """LLM-based HyDE — generates a hypothetical legal document.

    Asks an LLM to generate a hypothetical relevant legal answer/document
    for the query, then uses that as the search query.
    """

    HYDE_SYSTEM = (
        "You are a legal expert. Given a legal query, write a short hypothetical "
        "passage (3-5 sentences) that would appear in a relevant legal document — "
        "a statute section, case judgment, or legal commentary. Use formal legal "
        "language. This passage will be used to retrieve similar real documents."
    )

    def __init__(self, **kwargs):
        self.llm = LLMProvider(**kwargs)

    def transform(self, query: str) -> QueryTransformation:
        prompt = f"Legal query: {query}\n\nHypothetical relevant passage:"
        resp = self.llm.generate(prompt, system=self.HYDE_SYSTEM, temperature=0.3, max_tokens=400)
        hypothetical = resp.text.strip()
        # Use the hypothetical document as the search query
        return QueryTransformation(
            original=query,
            transformed=hypothetical,
            strategy="llm_hyde",
            hypothetical_document=hypothetical,
            latency_seconds=resp.latency_seconds,
            token_usage={"in": resp.tokens_in, "out": resp.tokens_out},
            cost_usd=resp.cost_usd,
        )
