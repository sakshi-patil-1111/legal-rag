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
    LLMQueryRewriteStrategy,
    LLMHyDEStrategy,
    QueryStrategy,
)
from .reranker import (
    CrossEncoderReranker,
    LLMReranker,
    NoOpReranker,
    Reranker,
    TokenOverlapReranker,
)
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
            k1=retrieval.get("k1", 1.6),
            b=retrieval.get("b", 0.7),
            ngram=retrieval.get("ngram", 1),
        )
    if rtype == "dense":
        return DenseRetriever(
            model_name=retrieval.get("model_name", "BAAI/bge-base-en-v1.5"),
            backend=retrieval.get("backend", "auto"),
            device=retrieval.get("device", "auto"),
            query_prompt=retrieval.get("query_prompt"),
            max_length=retrieval.get("max_length", 32768),
            dtype=retrieval.get("dtype"),
            query_device=retrieval.get("query_device"),
            cache_dir=retrieval.get("cache_dir", "data/cache"),
            batch_size=retrieval.get("batch_size", 32),
            show_progress=retrieval.get("show_progress", True),
        )
    if rtype == "hybrid":
        bm25 = BM25Retriever(
            k1=retrieval.get("bm25_k1", 1.5),
            b=retrieval.get("bm25_b", 0.75),
            ngram=retrieval.get("bm25_ngram", 1),
        )
        dense = DenseRetriever(
            model_name=retrieval.get("dense_model_name", "BAAI/bge-base-en-v1.5"),
            backend=retrieval.get("backend", "auto"),
            device=retrieval.get("device", "auto"),
            query_prompt=retrieval.get("query_prompt"),
            max_length=retrieval.get("max_length", 32768),
            dtype=retrieval.get("dtype"),
            query_device=retrieval.get("query_device"),
            cache_dir=retrieval.get("cache_dir", "data/cache"),
            batch_size=retrieval.get("batch_size", 32),
            show_progress=retrieval.get("show_progress", True),
        )
        return HybridRetriever(bm25, dense, k=retrieval.get("rrf_k", 60.0))
    raise ValueError(f"Unknown retriever type: {rtype}")


def build_query_strategy(name: str, **kwargs) -> QueryStrategy:
    if name == "direct":
        return DirectQueryStrategy()
    if name == "keyword":
        return KeywordExpansionQueryStrategy()
    if name == "hyde":
        return HyDEQueryStrategy()
    if name == "llm_rewrite":
        return LLMQueryRewriteStrategy(**kwargs)
    if name == "llm_hyde":
        return LLMHyDEStrategy(**kwargs)
    raise ValueError(f"Unknown query strategy: {name}")


def build_reranker(config: dict | None) -> Reranker:
    if not config or not config.get("enabled", False):
        return NoOpReranker()
    rtype = config.get("type", "token_overlap")
    if rtype == "token_overlap":
        return TokenOverlapReranker()
    if rtype == "cross_encoder":
        return CrossEncoderReranker(
            model_name=config.get("model_name", "cross-encoder/ms-marco-MiniLM-L-6-v2"),
            max_length=config.get("max_length", 512),
        )
    if rtype == "llm":
        return LLMReranker(
            model_name=config.get("model_name", "gpt-5-mini"),
            pool_size=config.get("pool_size", 20),
            query_chars=config.get("query_chars", 4000),
            doc_chars=config.get("doc_chars", 1000),
            provider=config.get("provider", "openai_compatible"),
            base_url=config.get("base_url", "https://api.openai.com/v1"),
            api_key_env=config.get("api_key_env", "OPENAI_API_KEY"),
            reasoning_effort=config.get("reasoning_effort"),
        )
    raise ValueError(f"Unknown reranker: {rtype}")
