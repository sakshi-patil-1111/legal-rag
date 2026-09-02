import hashlib
import json
import os
from pathlib import Path
from typing import Any

import numpy as np

from .base import Retriever

try:
    from sentence_transformers import SentenceTransformer

    ST_AVAILABLE = True
except ImportError:
    ST_AVAILABLE = False


def _cache_key(model_name: str, texts: list[str]) -> str:
    """Deterministic cache key from model name + text content hash."""
    h = hashlib.sha256()
    h.update(model_name.encode())
    for t in texts:
        h.update(t.encode())
    return h.hexdigest()[:32]


class DenseRetriever(Retriever):
    """Real dense retriever using sentence-transformers embeddings.

    Caches embeddings to disk so re-runs with the same model + corpus
    don't re-encode everything.

    Falls back to TF-IDF/SVD if sentence-transformers is not installed
    (kept for backward compatibility with tests / CI without the heavy dep).
    """

    def __init__(
        self,
        model_name: str = "BAAI/bge-base-en-v1.5",
        cache_dir: str | Path | None = "data/cache",
        batch_size: int = 32,
        show_progress: bool = True,
        random_state: int = 42,
    ):
        super().__init__()
        self.model_name = model_name
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self.batch_size = batch_size
        self.show_progress = show_progress
        self.random_state = random_state
        self._model: Any = None
        self._vectors: np.ndarray | None = None

        # Legacy TF-IDF fallback
        self._fallback: Any = None

    def _load_model(self) -> Any:
        if self._model is None:
            if not ST_AVAILABLE:
                raise RuntimeError(
                    "sentence-transformers is required for DenseRetriever. "
                    "Install with: pip install sentence-transformers"
                )
            self._model = SentenceTransformer(
                self.model_name,
                device="cpu",  # student compute — CPU by default
            )
        return self._model

    def _try_load_cache(self, key: str) -> np.ndarray | None:
        if self.cache_dir is None:
            return None
        cache_file = self.cache_dir / f"dense_{self.model_name.replace('/', '_')}_{key}.npy"
        if cache_file.exists():
            return np.load(cache_file)
        return None

    def _save_cache(self, key: str, vectors: np.ndarray) -> None:
        if self.cache_dir is None:
            return
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = self.cache_dir / f"dense_{self.model_name.replace('/', '_')}_{key}.npy"
        np.save(cache_file, vectors)

    def index(self, items: list[Any]) -> None:
        self.items = items
        self._chunk_ids = [self._chunk_id(d) for d in items]
        texts = [self._text(d) for d in items]

        if ST_AVAILABLE:
            model = self._load_model()
            key = _cache_key(self.model_name, texts)

            cached = self._try_load_cache(key)
            if cached is not None:
                self._vectors = cached
            else:
                self._vectors = model.encode(
                    texts,
                    batch_size=self.batch_size,
                    show_progress_bar=self.show_progress,
                    normalize_embeddings=True,
                    convert_to_numpy=True,
                )
                self._save_cache(key, self._vectors)
        else:
            # Fallback: TF-IDF + SVD (for tests without heavy deps)
            self._fallback = _TfidfFallback()
            self._fallback.index(texts, self.random_state)

    def search(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        if self._vectors is not None:
            return self._search_st(query, top_k, dedup=True)
        elif self._fallback is not None:
            return self._fallback.search(query, self.items, self._external_id, top_k, dedup=True)
        raise RuntimeError("Retriever has not been indexed.")

    def search_chunks(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        if self._vectors is not None:
            return self._search_st(query, top_k, dedup=False)
        elif self._fallback is not None:
            return self._fallback.search(query, self.items, self._chunk_id, top_k, dedup=False)
        raise RuntimeError("Retriever has not been indexed.")

    def _search_st(
        self, query: str, top_k: int, dedup: bool,
    ) -> list[tuple[str, float]]:
        model = self._load_model()
        q_vec = model.encode(
            [query], normalize_embeddings=True, convert_to_numpy=True,
        )
        scores = (self._vectors @ q_vec.T).ravel()
        order = np.argsort(-scores)

        if not dedup:
            return [(self._chunk_ids[idx], float(scores[idx])) for idx in order[:top_k]]

        seen: set[str] = set()
        deduped: list[tuple[str, float]] = []
        for idx in order:
            item = self.items[idx]
            ext_id = self._external_id(item)
            if ext_id not in seen:
                seen.add(ext_id)
                deduped.append((ext_id, float(scores[idx])))
        return deduped[:top_k]


class _TfidfFallback:
    """TF-IDF + SVD fallback for environments without sentence-transformers."""

    def __init__(self):
        from sklearn.decomposition import TruncatedSVD
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.preprocessing import normalize
        self._TfidfVectorizer = TfidfVectorizer
        self._TruncatedSVD = TruncatedSVD
        self._normalize = normalize
        self._vectorizer = None
        self._svd = None
        self._vectors = None

    def index(self, texts: list[str], random_state: int = 42) -> None:
        self._vectorizer = self._TfidfVectorizer(stop_words="english")
        tfidf = self._vectorizer.fit_transform(texts)
        n_features = tfidf.shape[1]
        n_docs = tfidf.shape[0]
        n_comp = max(1, min(50, n_features - 1, n_docs - 1))
        self._svd = self._TruncatedSVD(n_components=n_comp, random_state=random_state)
        self._vectors = self._svd.fit_transform(tfidf)
        self._normalize(self._vectors, norm="l2", copy=False)

    def search(
        self, query: str, items: list[Any], id_fn, top_k: int, dedup: bool,
    ) -> list[tuple[str, float]]:
        q_tfidf = self._vectorizer.transform([query])
        q_vec = self._svd.transform(q_tfidf)
        self._normalize(q_vec, norm="l2", copy=False)
        scores = (self._vectors @ q_vec.T).ravel()
        order = np.argsort(-scores)

        if not dedup:
            return [(id_fn(items[idx]), float(scores[idx])) for idx in order[:top_k]]

        seen: set[str] = set()
        deduped: list[tuple[str, float]] = []
        for idx in order:
            ext_id = id_fn(items[idx])
            if ext_id not in seen:
                seen.add(ext_id)
                deduped.append((ext_id, float(scores[idx])))
        return deduped[:top_k]
