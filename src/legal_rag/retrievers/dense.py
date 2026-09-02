import hashlib
import os
import platform
from pathlib import Path
from typing import Any

import numpy as np

from .base import Retriever

# --- MLX (Apple Silicon fast path) ---
try:
    import mlx.core as mx
    from mlx_embeddings.utils import load as mlx_load, generate as mlx_generate

    MLX_AVAILABLE = True
except ImportError:
    MLX_AVAILABLE = False

# --- sentence-transformers (cross-platform fallback) ---
try:
    from sentence_transformers import SentenceTransformer

    ST_AVAILABLE = True
except ImportError:
    ST_AVAILABLE = False


def _is_apple_silicon() -> bool:
    return platform.system() == "Darwin" and platform.machine() == "arm64"


def _cache_key(model_name: str, texts: list[str]) -> str:
    """Deterministic cache key from model name + text content hash."""
    h = hashlib.sha256()
    h.update(model_name.encode())
    for t in texts:
        h.update(t.encode())
    return h.hexdigest()[:32]


class DenseRetriever(Retriever):
    """Dense retriever using embedding models.

    Backend priority on Apple Silicon:
      1. MLX + mlx-embeddings (fast, uses GPU/neural engine)
      2. sentence-transformers (CPU fallback)

    Backend priority elsewhere:
      1. sentence-transformers
      2. TF-IDF/SVD (last resort for tests without heavy deps)

    Caches embeddings to disk so re-runs with the same model + corpus
    don't re-encode everything.
    """

    def __init__(
        self,
        model_name: str = "BAAI/bge-base-en-v1.5",
        cache_dir: str | Path | None = "data/cache",
        batch_size: int = 32,
        show_progress: bool = True,
        random_state: int = 42,
        backend: str = "auto",  # auto | mlx | sentence_transformers | tfidf
    ):
        super().__init__()
        self.model_name = model_name
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self.batch_size = batch_size
        self.show_progress = show_progress
        self.random_state = random_state
        self._backend = self._select_backend(backend)
        self._model: Any = None
        self._tokenizer: Any = None
        self._vectors: np.ndarray | None = None
        self._fallback: Any = None  # TF-IDF fallback

    def _select_backend(self, requested: str) -> str:
        if requested == "auto":
            if MLX_AVAILABLE and _is_apple_silicon():
                return "mlx"
            if ST_AVAILABLE:
                return "sentence_transformers"
            return "tfidf"
        if requested == "mlx" and not MLX_AVAILABLE:
            raise RuntimeError("MLX not available. Install with: pip install mlx-embeddings")
        if requested == "sentence_transformers" and not ST_AVAILABLE:
            raise RuntimeError(
                "sentence-transformers not available. "
                "Install with: pip install sentence-transformers"
            )
        return requested

    def _load_model(self) -> None:
        if self._backend == "mlx":
            if self._model is None:
                self._model, self._tokenizer = mlx_load(self.model_name)
        elif self._backend == "sentence_transformers":
            if self._model is None:
                self._model = SentenceTransformer(self.model_name, device="cpu")
        else:
            # TF-IDF fallback — lazy init in index()
            pass

    def _try_load_cache(self, key: str) -> np.ndarray | None:
        if self.cache_dir is None:
            return None
        safe_name = self.model_name.replace("/", "_")
        cache_file = self.cache_dir / f"dense_{safe_name}_{key}.npy"
        if cache_file.exists():
            return np.load(cache_file)
        return None

    def _save_cache(self, key: str, vectors: np.ndarray) -> None:
        if self.cache_dir is None:
            return
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        safe_name = self.model_name.replace("/", "_")
        cache_file = self.cache_dir / f"dense_{safe_name}_{key}.npy"
        np.save(cache_file, vectors)

    def _encode_mlx(self, texts: list[str]) -> np.ndarray:
        all_vecs = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            embs = mlx_generate(self._model, self._tokenizer, batch)
            mx.eval(embs)
            vecs = embs.text_embeds
            if vecs is None:
                vecs = embs.pooler_output
            if vecs is None:
                vecs = embs.last_hidden_state.mean(axis=1)
            all_vecs.append(np.array(mx.array(vecs), dtype=np.float32))
        result = np.concatenate(all_vecs, axis=0)
        # L2 normalize
        norms = np.linalg.norm(result, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return result / norms

    def _encode_st(self, texts: list[str]) -> np.ndarray:
        result = self._model.encode(
            texts,
            batch_size=self.batch_size,
            show_progress_bar=self.show_progress,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return result.astype(np.float32)

    def index(self, items: list[Any]) -> None:
        self.items = items
        self._chunk_ids = [self._chunk_id(d) for d in items]
        texts = [self._text(d) for d in items]

        if self._backend == "tfidf":
            self._fallback = _TfidfFallback()
            self._fallback.index(texts, self.random_state)
            return

        self._load_model()
        key = _cache_key(self.model_name, texts)

        cached = self._try_load_cache(key)
        if cached is not None:
            self._vectors = cached
        else:
            if self._backend == "mlx":
                self._vectors = self._encode_mlx(texts)
            else:
                self._vectors = self._encode_st(texts)
            self._save_cache(key, self._vectors)

    def _encode_query(self, query: str) -> np.ndarray:
        if self._backend == "mlx":
            return self._encode_mlx([query])
        else:
            return self._encode_st([query])

    def search(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        if self._vectors is not None:
            return self._search_dense(query, top_k, dedup=True)
        elif self._fallback is not None:
            return self._fallback.search(query, self.items, self._external_id, top_k, dedup=True)
        raise RuntimeError("Retriever has not been indexed.")

    def search_chunks(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        if self._vectors is not None:
            return self._search_dense(query, top_k, dedup=False)
        elif self._fallback is not None:
            return self._fallback.search(query, self.items, self._chunk_id, top_k, dedup=False)
        raise RuntimeError("Retriever has not been indexed.")

    def _search_dense(
        self, query: str, top_k: int, dedup: bool,
    ) -> list[tuple[str, float]]:
        q_vec = self._encode_query(query)
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
    """TF-IDF + SVD fallback for environments without embedding libraries."""

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
