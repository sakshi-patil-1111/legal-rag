import time
from abc import ABC, abstractmethod
from collections import Counter
from typing import Any

from .tokenization import tokenize

try:
    from sentence_transformers import CrossEncoder

    CE_AVAILABLE = True
except ImportError:
    CE_AVAILABLE = False


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


class CrossEncoderReranker(Reranker):
    """Cross-encoder reranker using sentence-transformers.

    Scores each (query, document) pair with a cross-encoder model
    and re-sorts candidates by the cross-encoder score.
    """

    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        max_length: int = 512,
    ):
        self.model_name = model_name
        self.max_length = max_length
        self._model: Any = None

    def _load_model(self) -> Any:
        if self._model is None:
            if not CE_AVAILABLE:
                raise RuntimeError(
                    "sentence-transformers is required for CrossEncoderReranker. "
                    "Install with: pip install sentence-transformers"
                )
            self._model = CrossEncoder(self.model_name, max_length=self.max_length)
        return self._model

    def rerank(
        self,
        query: str,
        candidates: list[tuple[str, float]],
        texts: dict[str, str],
        top_k: int,
    ) -> list[tuple[str, float]]:
        if not candidates:
            return []
        model = self._load_model()

        pairs = [(query, texts.get(doc_id, "")) for doc_id, _ in candidates]
        scores = model.predict(pairs, show_progress_bar=False)

        reranked = [
            (doc_id, float(score))
            for (doc_id, _), score in zip(candidates, scores)
        ]
        reranked.sort(key=lambda x: x[1], reverse=True)
        return reranked[:top_k]
