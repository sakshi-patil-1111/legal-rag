import math
from collections import Counter
from typing import Callable

from .schemas import LegalDocument


class SimpleBM25:
    def __init__(
        self,
        documents: list[LegalDocument],
        tokenize: Callable[[str], list[str]],
        k1: float = 1.5,
        b: float = 0.75,
    ):
        self.documents = documents
        self.tokenize = tokenize
        self.k1 = k1
        self.b = b
        self.doc_ids = [d.doc_id for d in documents]
        self.tokenized = [tokenize(d.raw_text) for d in documents]
        self.N = len(self.documents)
        self.avgdl = (
            sum(len(t) for t in self.tokenized) / self.N if self.N else 0.0
        )
        self.df: dict[str, int] = {}
        for tokens in self.tokenized:
            for token in set(tokens):
                self.df[token] = self.df.get(token, 0) + 1

    def _idf(self, token: str) -> float:
        df = self.df.get(token, 0)
        if df == 0:
            return 0.0
        return math.log((self.N - df + 0.5) / (df + 0.5) + 1.0)

    def score(self, query_tokens: list[str], doc_index: int) -> float:
        doc = self.tokenized[doc_index]
        doc_len = len(doc)
        freqs = Counter(doc)
        score = 0.0
        for token in query_tokens:
            if token not in self.df:
                continue
            f = freqs.get(token, 0)
            denom = f + self.k1 * (1.0 - self.b + self.b * (doc_len / self.avgdl))
            score += self._idf(token) * (f * (self.k1 + 1.0)) / denom
        return score

    def retrieve(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        query_tokens = self.tokenize(query)
        scored = [
            (self.doc_ids[i], self.score(query_tokens, i))
            for i in range(self.N)
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def retrieve_with_idx(self, query: str, top_k: int = 10) -> list[tuple[int, float]]:
        """Return (index, score) pairs, sorted by score descending."""
        query_tokens = self.tokenize(query)
        scored = [
            (i, self.score(query_tokens, i))
            for i in range(self.N)
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]
