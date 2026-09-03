from typing import Any

from .base import Retriever


def _rank_map(results: list[tuple[str, float]]) -> dict[str, int]:
    return {doc_id: rank for rank, (doc_id, _) in enumerate(results, start=1)}


class HybridRetriever(Retriever):
    def __init__(
        self,
        retriever_a: Retriever,
        retriever_b: Retriever,
        k: float = 60.0,
    ):
        super().__init__()
        self.retriever_a = retriever_a
        self.retriever_b = retriever_b
        self.k = k

    def index(self, items: list[Any]) -> None:
        self.items = items
        self._chunk_ids = [self._chunk_id(d) for d in items]
        self.retriever_a.index(items)
        self.retriever_b.index(items)

    def search(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        results_a = self.retriever_a.search(query, top_k=top_k * 2)
        results_b = self.retriever_b.search(query, top_k=top_k * 2)

        rank_a = _rank_map(results_a)
        rank_b = _rank_map(results_b)
        ids = set(rank_a) | set(rank_b)

        fused: list[tuple[str, float]] = []
        for doc_id in ids:
            score = 0.0
            if doc_id in rank_a:
                score += 1.0 / (self.k + rank_a[doc_id])
            if doc_id in rank_b:
                score += 1.0 / (self.k + rank_b[doc_id])
            fused.append((doc_id, score))

        fused.sort(key=lambda x: x[1], reverse=True)
        return fused[:top_k]

    def search_chunks(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        results_a = self.retriever_a.search_chunks(query, top_k=top_k * 2)
        results_b = self.retriever_b.search_chunks(query, top_k=top_k * 2)

        rank_a = _rank_map(results_a)
        rank_b = _rank_map(results_b)
        ids = set(rank_a) | set(rank_b)

        fused: list[tuple[str, float]] = []
        for chunk_id in ids:
            score = 0.0
            if chunk_id in rank_a:
                score += 1.0 / (self.k + rank_a[chunk_id])
            if chunk_id in rank_b:
                score += 1.0 / (self.k + rank_b[chunk_id])
            fused.append((chunk_id, score))

        fused.sort(key=lambda x: x[1], reverse=True)
        return fused[:top_k]
