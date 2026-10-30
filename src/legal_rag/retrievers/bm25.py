import hashlib
from pathlib import Path
from typing import Any

import bm25s

from .base import Retriever


class BM25Retriever(Retriever):
    def __init__(
        self,
        k1: float = 1.6,
        b: float = 0.7,
        ngram: int = 1,
        cache_dir: str | Path | None = None,
    ):
        super().__init__()
        self.k1 = k1
        self.b = b
        self.ngram = ngram
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self._bm25: bm25s.BM25 | None = None
        self._corpus: list[str] = []

    def _cache_path(self) -> Path:
        h = hashlib.sha256()
        h.update(f"k1={self.k1};b={self.b};ngram={self.ngram}".encode())
        for t in self._corpus:
            h.update(t.encode())
        return self.cache_dir / f"bm25_{h.hexdigest()[:24]}"

    def _tokenize(self, texts: list[str]):
        if self.ngram <= 1:
            return bm25s.tokenize(texts, stopwords="en", show_progress=False)
        words = bm25s.tokenize(
            texts, stopwords=[], return_ids=False, show_progress=False
        )
        n = self.ngram
        docs = [
            " ".join("_".join(w[i : i + n]) for i in range(len(w) - n + 1))
            for w in words
        ]
        return bm25s.tokenize(docs, stopwords=[], show_progress=False)

    def index(self, items: list[Any]) -> None:
        self.items = items
        self._chunk_ids = [self._chunk_id(d) for d in items]
        self._corpus = [self._text(d) for d in items]
        if self.cache_dir is not None:
            cache_path = self._cache_path()
            if cache_path.exists():
                self._bm25 = bm25s.BM25.load(str(cache_path), show_progress=False)
                return
        tokens = self._tokenize(self._corpus)
        self._bm25 = bm25s.BM25(k1=self.k1, b=self.b)
        self._bm25.index(tokens, show_progress=False)
        if self.cache_dir is not None:
            cache_path.mkdir(parents=True, exist_ok=True)
            self._bm25.save(str(cache_path), show_progress=False)

    def _retrieve(self, query: str, top_k: int) -> list[tuple[int, float]]:
        k = min(top_k, len(self.items))
        q_tokens = self._tokenize([query])
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
