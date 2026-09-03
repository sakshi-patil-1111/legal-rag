from typing import Any

import bm25s

from .base import Retriever


class BM25Retriever(Retriever):
    def __init__(self, k1: float = 1.6, b: float = 0.7):
        super().__init__()
        self.k1 = k1
        self.b = b
        self._bm25: bm25s.BM25 | None = None
        self._corpus: list[str] = []

    def index(self, items: list[Any]) -> None:
        self.items = items
        self._chunk_ids = [self._chunk_id(d) for d in items]
        self._corpus = [self._text(d) for d in items]
        tokens = bm25s.tokenize(self._corpus, stopwords="en", show_progress=False)
        self._bm25 = bm25s.BM25(k1=self.k1, b=self.b)
        self._bm25.index(tokens, show_progress=False)

    def _retrieve(self, query: str, top_k: int) -> list[tuple[int, float]]:
        k = min(top_k, len(self.items))
        q_tokens = bm25s.tokenize([query], stopwords="en", show_progress=False)
        results, scores = self._bm25.retrieve(q_tokens, k=k, corpus=None, show_progress=False)
        return [(int(i), float(s)) for i, s in zip(results[0], scores[0])]

    def search(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        hits = self._retrieve(query, top_k)
        seen: set[str] = set()
        out: list[tuple[str, float]] = []
        for idx, score in hits:
            ext_id = self._external_id(self.items[idx])
            if ext_id not in seen:
                seen.add(ext_id)
                out.append((ext_id, score))
        return out[:top_k]

    def search_chunks(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        hits = self._retrieve(query, top_k)
        return [(self._chunk_ids[idx], score) for idx, score in hits]
