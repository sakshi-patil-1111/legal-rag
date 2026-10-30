import json
import os
import re
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


class LLMReranker(Reranker):
    """Listwise LLM reranker.

    Presents the top ``pool_size`` candidates as numbered snippets and asks
    the model for a JSON array of snippet indices in decreasing relevance.
    Any candidates the model omits keep their original relative order; on
    API or parse failure the original ranking is returned unchanged.
    """

    SYSTEM = (
        "You are a legal retrieval reranker. Given a legal query and numbered "
        "document snippets, return ONLY a JSON array of the snippet numbers "
        "ordered from most to least relevant. Include every number exactly once."
    )

    def __init__(
        self,
        model_name: str = "gpt-5-mini",
        pool_size: int = 20,
        query_chars: int = 4000,
        doc_chars: int = 1000,
        provider: str = "openai_compatible",
        base_url: str = "https://api.openai.com/v1",
        api_key_env: str = "OPENAI_API_KEY",
        reasoning_effort: str | None = None,
        max_retries: int = 2,
    ):
        self.model_name = model_name
        self.pool_size = pool_size
        self.query_chars = query_chars
        self.doc_chars = doc_chars
        self.reasoning_effort = reasoning_effort
        self.max_retries = max_retries
        self.calls = 0
        self.tokens_in = 0
        self.tokens_out = 0
        self.failures = 0
        from .llm import LLMProvider

        self._llm = LLMProvider(
            provider=provider,
            api_key=os.getenv(api_key_env, ""),
            base_url=base_url,
            model=model_name,
        )

    def _build_prompt(self, query: str, snippets: list[str]) -> str:
        parts = [f"QUERY:\n{query[: self.query_chars]}\n\nDOCUMENTS:"]
        for i, snip in enumerate(snippets, 1):
            parts.append(f"\n[{i}] {snip}")
        parts.append(
            "\n\nReturn the JSON array of document numbers, most relevant first."
        )
        return "".join(parts)

    def _parse_order(self, text: str, n: int) -> list[int] | None:
        m = re.search(r"\[[\d,\s]*\]", text)
        if not m:
            return None
        try:
            order = [int(x) for x in json.loads(m.group(0))]
        except (ValueError, TypeError):
            return None
        if not order or any(i < 1 or i > n for i in order):
            return None
        return order

    def rerank(
        self,
        query: str,
        candidates: list[tuple[str, float]],
        texts: dict[str, str],
        top_k: int,
    ) -> list[tuple[str, float]]:
        if not candidates:
            return []
        pool = candidates[: self.pool_size]
        rest = candidates[self.pool_size :]
        snippets = [texts.get(doc_id, "")[: self.doc_chars] for doc_id, _ in pool]
        prompt = self._build_prompt(query, snippets)

        order = None
        for _ in range(self.max_retries):
            try:
                resp = self._llm.generate(
                    prompt,
                    system=self.SYSTEM,
                    temperature=0.0,
                    max_tokens=1024,
                    reasoning_effort=self.reasoning_effort,
                )
                self.calls += 1
                self.tokens_in += resp.tokens_in
                self.tokens_out += resp.tokens_out
                order = self._parse_order(resp.text, len(pool))
                if order:
                    break
            except Exception:  # noqa: BLE001
                pass
            time.sleep(1.0)
        if order is None:
            self.failures += 1
            return candidates[:top_k]

        seen: set[int] = set()
        ranked: list[tuple[str, float]] = []
        for pos, idx in enumerate(order):
            if idx in seen:
                continue
            seen.add(idx)
            doc_id = pool[idx - 1][0]
            ranked.append((doc_id, float(len(pool) - pos)))
        for i, (doc_id, _) in enumerate(pool):
            if (i + 1) not in seen:
                ranked.append((doc_id, 0.0))
        ranked.extend((doc_id, 0.0) for doc_id, _ in rest)
        return ranked[:top_k]
