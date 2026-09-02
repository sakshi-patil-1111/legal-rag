import numpy as np
from typing import Any

from .base import Retriever

try:
    from sklearn.decomposition import TruncatedSVD
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.preprocessing import normalize

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class DenseRetriever(Retriever):
    def __init__(self, n_components: int = 50, random_state: int = 42):
        super().__init__()
        self.n_components = n_components
        self.random_state = random_state
        self._vectorizer: Any = None
        self._svd: Any = None
        self._vectors: np.ndarray | None = None

    def _n_comp(self, n_features: int, n_docs: int) -> int:
        return max(
            1,
            min(
                self.n_components,
                n_features - 1,
                n_docs - 1,
            ),
        )

    def index(self, items: list[Any]) -> None:
        if not SKLEARN_AVAILABLE:
            raise RuntimeError("scikit-learn is required for the dense retriever.")
        self.items = items
        texts = [self._text(d) for d in items]
        self._vectorizer = TfidfVectorizer(stop_words="english")
        tfidf = self._vectorizer.fit_transform(texts)
        n_features = tfidf.shape[1]
        n_docs = tfidf.shape[0]
        n_comp = self._n_comp(n_features, n_docs)
        self._svd = TruncatedSVD(
            n_components=n_comp, random_state=self.random_state
        )
        self._vectors = self._svd.fit_transform(tfidf)
        normalize(self._vectors, norm="l2", copy=False)

    def search(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        if self._svd is None or self._vectors is None:
            raise RuntimeError("Retriever has not been indexed.")
        q_tfidf = self._vectorizer.transform([query])
        q_vec = self._svd.transform(q_tfidf)
        normalize(q_vec, norm="l2", copy=False)
        scores = (self._vectors @ q_vec.T).ravel()
        order = np.argsort(-scores)

        seen: set[str] = set()
        deduped: list[tuple[str, float]] = []
        for idx in order:
            item = self.items[idx]
            ext_id = self._external_id(item)
            if ext_id not in seen:
                seen.add(ext_id)
                deduped.append((ext_id, float(scores[idx])))
        return deduped[:top_k]
