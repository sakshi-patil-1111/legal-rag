from abc import ABC, abstractmethod
from collections import Counter
from typing import Any

from .tokenization import tokenize


class Reranker(ABC):
    @abstractmethod
    def rerank(
        self,
        query: str,
        candidates: list[tuple[str, float]],
        texts: dict[str, str],
        top_k: int,
    ) -> list[tuple[str, float]]:
        ...


class NoOpReranker(Reranker):
    def rerank(
        self,
        query: str,
        candidates: list[tuple[str, float]],
        texts: dict[str, str],
        top_k: int,
    ) -> list[tuple[str, float]]:
        return candidates[:top_k]


class TokenOverlapReranker(Reranker):
    def _jaccard(self, a: set[str], b: set[str]) -> float:
        if not a and not b:
            return 0.0
        return len(a & b) / len(a | b)

    def rerank(
        self,
        query: str,
        candidates: list[tuple[str, float]],
        texts: dict[str, str],
        top_k: int,
    ) -> list[tuple[str, float]]:
        q_tokens = set(tokenize(query))
        scored: list[tuple[str, float]] = []
        for doc_id, _ in candidates:
            text = texts.get(doc_id, "")
            d_tokens = set(tokenize(text))
            overlap = self._jaccard(q_tokens, d_tokens)
            scored.append((doc_id, overlap))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]
