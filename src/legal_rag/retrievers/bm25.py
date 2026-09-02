from typing import Any

from ..bm25 import SimpleBM25
from ..tokenization import tokenize
from .base import Retriever


class BM25Retriever(Retriever):
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        super().__init__()
        self.k1 = k1
        self.b = b
        self._index: SimpleBM25 | None = None

    def index(self, items: list[Any]) -> None:
        self.items = items
        self._chunk_ids = [self._chunk_id(d) for d in items]
        docs = [
            type("D", (), {"doc_id": self._external_id(d), "raw_text": self._text(d)})()
            for d in items
        ]
        self._index = SimpleBM25(docs, tokenize, k1=self.k1, b=self.b)

    def search(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        if self._index is None:
            raise RuntimeError("Retriever has not been indexed.")
        results = self._index.retrieve(query, top_k=top_k)
        seen: set[str] = set()
        deduped: list[tuple[str, float]] = []
        for doc_id, score in results:
            if doc_id not in seen:
                seen.add(doc_id)
                deduped.append((doc_id, score))
        return deduped[:top_k]

    def search_chunks(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        if self._index is None:
            raise RuntimeError("Retriever has not been indexed.")
        results = self._index.retrieve_with_idx(query, top_k=top_k)
        return [(self._chunk_ids[idx], score) for idx, score in results]
