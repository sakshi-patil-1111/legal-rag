from .chunking import (
    Chunker,
    FixedCharChunker,
    FixedTokenChunker,
    RecursiveChunker,
    WholeDocumentChunker,
)
from .query import (
    DirectQueryStrategy,
    HyDEQueryStrategy,
    KeywordExpansionQueryStrategy,
    QueryStrategy,
)
from .reranker import NoOpReranker, Reranker, TokenOverlapReranker
from .retrievers import BM25Retriever, DenseRetriever, HybridRetriever, Retriever


def build_chunker(strategy: str, **kwargs) -> Chunker:
    if strategy == "whole":
        return WholeDocumentChunker()
    if strategy == "fixed_token":
        size = kwargs.get("size", 512)
        overlap = kwargs.get("overlap", 0)
        return FixedTokenChunker(size=size, overlap=overlap)
    if strategy == "fixed_char":
        size = kwargs.get("size", 1024)
        overlap = kwargs.get("overlap", 0)
        return FixedCharChunker(size=size, overlap=overlap)
    if strategy == "recursive":
        size = kwargs.get("size", 512)
        overlap = kwargs.get("overlap", 0)
        return RecursiveChunker(size=size, overlap=overlap)
    raise ValueError(f"Unknown chunking strategy: {strategy}")


def build_retriever(retrieval: dict) -> Retriever:
    rtype = retrieval.get("type", "bm25")
    if rtype == "bm25":
        return BM25Retriever(
            k1=retrieval.get("k1", 1.5),
            b=retrieval.get("b", 0.75),
        )
    if rtype == "dense":
        return DenseRetriever(
            n_components=retrieval.get("n_components", 50),
            random_state=retrieval.get("random_state", 42),
        )
    if rtype == "hybrid":
        bm25 = BM25Retriever(
            k1=retrieval.get("bm25_k1", 1.5),
            b=retrieval.get("bm25_b", 0.75),
        )
        dense = DenseRetriever(
            n_components=retrieval.get("dense_n_components", 50),
            random_state=retrieval.get("dense_random_state", 42),
        )
        return HybridRetriever(bm25, dense, k=retrieval.get("rrf_k", 60.0))
    raise ValueError(f"Unknown retriever type: {rtype}")


def build_query_strategy(name: str) -> QueryStrategy:
    if name == "direct":
        return DirectQueryStrategy()
    if name == "keyword":
        return KeywordExpansionQueryStrategy()
    if name == "hyde":
        return HyDEQueryStrategy()
    raise ValueError(f"Unknown query strategy: {name}")


def build_reranker(config: dict | None) -> Reranker:
    if not config or not config.get("enabled", False):
        return NoOpReranker()
    rtype = config.get("type", "token_overlap")
    if rtype == "token_overlap":
        return TokenOverlapReranker()
    raise ValueError(f"Unknown reranker: {rtype}")
