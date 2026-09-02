import time
from pathlib import Path
from typing import Any, Literal

from .chunking import Chunker
from .metrics import evaluate_query, evaluate_query_snippet
from .query import QueryStrategy
from .reranker import Reranker
from .retrievers.base import Retriever
from .schemas import LegalQuery


def _texts_by_id(items: list[Any]) -> dict[str, str]:
    texts: dict[str, str] = {}
    for item in items:
        ext = item.parent_doc_id if hasattr(item, "parent_doc_id") else None
        if ext is None:
            ext = item.doc_id
        text = getattr(item, "text", getattr(item, "raw_text", ""))
        if ext not in texts or len(text) > len(texts[ext]):
            texts[ext] = text
    return texts


class RetrievalEvaluator:
    def __init__(
        self,
        chunker: Chunker,
        retriever: Retriever,
        query_strategy: QueryStrategy | None = None,
        reranker: Reranker | None = None,
    ):
        self.chunker = chunker
        self.retriever = retriever
        self.query_strategy = query_strategy
        self.reranker = reranker or None
        self.items: list[Any] = []
        self.chunk_map: dict[str, Any] = {}

    def index(self, documents: list[Any]) -> dict[str, Any]:
        self.items = self.chunker.chunk(documents)
        self.retriever.index(self.items)
        self.texts = _texts_by_id(self.items)
        self.chunk_map = {item.chunk_id: item for item in self.items if hasattr(item, "chunk_id")}
        return {
            "n_documents": len(documents),
            "n_chunks": len(self.items),
        }

    def evaluate(
        self,
        queries: list[LegalQuery],
        top_k: int = 10,
        final_k: int | None = None,
        ks: tuple[int, ...] = (1, 3, 5, 10),
        eval_mode: Literal["document", "snippet", "both"] = "document",
    ) -> dict[str, Any]:
        final_k = final_k or top_k
        query_results = []
        total_doc_recall = {f"recall@{k}": 0.0 for k in ks}
        total_doc_mrr = 0.0
        total_snippet = {f"snippet_recall@{k}": 0.0 for k in ks}
        total_snippet |= {f"snippet_precision@{k}": 0.0 for k in ks}
        n_snippet_queries = 0

        start = time.perf_counter()
        for query in queries:
            q_text = query.text
            q_transform = None
            if self.query_strategy:
                tq = self.query_strategy.transform(q_text)
                q_text = tq.transformed
                q_transform = tq.to_dict() if hasattr(tq, "to_dict") else vars(tq)

            # --- Document-level search (deduped to parent doc) ---
            doc_predictions = self.retriever.search(q_text, top_k=top_k)
            if self.reranker:
                doc_predictions = self.reranker.rerank(
                    q_text, doc_predictions, self.texts, top_k=final_k,
                )

            # --- Chunk-level search (for snippet eval) ---
            chunk_predictions = []
            snippets = query.metadata.get("snippets", [])
            if eval_mode in ("snippet", "both") and snippets:
                chunk_predictions = self.retriever.search_chunks(q_text, top_k=top_k)
                if self.reranker:
                    chunk_predictions = self.reranker.rerank(
                        q_text, chunk_predictions, self.texts, top_k=final_k,
                    )

            # --- Document-level metrics ---
            doc_metrics = {}
            if eval_mode in ("document", "both"):
                doc_metrics = evaluate_query(doc_predictions, query.ground_truth, ks=ks)
                for k in ks:
                    total_doc_recall[f"recall@{k}"] += doc_metrics[f"recall@{k}"]
                total_doc_mrr += doc_metrics["mrr"]

            # --- Snippet-level metrics ---
            snippet_metrics = {}
            if eval_mode in ("snippet", "both") and snippets:
                snippet_metrics = evaluate_query_snippet(
                    chunk_predictions, snippets, self.chunk_map, ks=ks,
                )
                for k in ks:
                    total_snippet[f"snippet_recall@{k}"] += snippet_metrics[f"snippet_recall@{k}"]
                    total_snippet[f"snippet_precision@{k}"] += snippet_metrics[f"snippet_precision@{k}"]
                n_snippet_queries += 1

            query_results.append({
                "qid": query.qid,
                "text": query.text,
                "transformed": q_transform,
                "doc_predictions": doc_predictions if eval_mode in ("document", "both") else None,
                "chunk_predictions": chunk_predictions if eval_mode in ("snippet", "both") else None,
                "ground_truth": query.ground_truth,
                "snippets": snippets if snippets else None,
                "doc_metrics": doc_metrics or None,
                "snippet_metrics": snippet_metrics or None,
            })

        latency = time.perf_counter() - start
        n = len(queries) if queries else 1

        aggregated: dict[str, Any] = {
            "n_queries": len(queries),
            "top_k": top_k,
            "final_k": final_k,
            "eval_mode": eval_mode,
            "latency_seconds": latency,
            "index_stats": {"n_chunks": len(self.items)},
        }

        if eval_mode in ("document", "both"):
            aggregated["metrics"] = {k: v / n for k, v in total_doc_recall.items()} | {"mrr": total_doc_mrr / n}

        if eval_mode in ("snippet", "both"):
            ns = n_snippet_queries if n_snippet_queries else 1
            aggregated["snippet_metrics"] = {k: v / ns for k, v in total_snippet.items()}
            aggregated["n_snippet_queries"] = n_snippet_queries

        aggregated["per_query"] = query_results
        return aggregated
