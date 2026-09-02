import time
from pathlib import Path
from typing import Any

from .chunking import Chunker
from .metrics import evaluate_query
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

    def index(self, documents: list[Any]) -> dict[str, Any]:
        self.items = self.chunker.chunk(documents)
        self.retriever.index(self.items)
        self.texts = _texts_by_id(self.items)
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
    ) -> dict[str, Any]:
        final_k = final_k or top_k
        query_results = []
        total_recall = {f"recall@{k}": 0.0 for k in ks}
        total_mrr = 0.0

        start = time.perf_counter()
        for query in queries:
            q_text = query.text
            q_transform = None
            if self.query_strategy:
                tq = self.query_strategy.transform(q_text)
                q_text = tq.transformed
                q_transform = tq.to_dict() if hasattr(tq, "to_dict") else vars(tq)

            predictions = self.retriever.search(q_text, top_k=top_k)

            if self.reranker:
                predictions = self.reranker.rerank(
                    q_text,
                    predictions,
                    self.texts,
                    top_k=final_k,
                )

            metrics = evaluate_query(predictions, query.ground_truth, ks=ks)
            for k in ks:
                total_recall[f"recall@{k}"] += metrics[f"recall@{k}"]
            total_mrr += metrics["mrr"]

            query_results.append({
                "qid": query.qid,
                "text": query.text,
                "transformed": q_transform,
                "predictions": predictions,
                "ground_truth": query.ground_truth,
                "metrics": metrics,
            })

        latency = time.perf_counter() - start
        n = len(queries) if queries else 1

        return {
            "n_queries": len(queries),
            "top_k": top_k,
            "final_k": final_k,
            "latency_seconds": latency,
            "index_stats": {"n_chunks": len(self.items)},
            "metrics": {k: v / n for k, v in total_recall.items()}
            | {"mrr": total_mrr / n},
            "per_query": query_results,
        }
