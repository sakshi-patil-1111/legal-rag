import hashlib
import json
import platform
import subprocess
import time
import uuid
from datetime import datetime, timezone
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


def _git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def _make_experiment_id(config: dict | None = None) -> str:
    if config and config.get("experiment_name"):
        base = config["experiment_name"]
    else:
        base = uuid.uuid4().hex[:8]
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return f"{base}_{ts}"


def _reproducibility_meta(config: dict | None = None, seed: int = 42) -> dict[str, Any]:
    return {
        "experiment_id": _make_experiment_id(config),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "seed": seed,
        "config_hash": hashlib.sha256(
            json.dumps(config or {}, sort_keys=True).encode()
        ).hexdigest()[:16],
    }


class RetrievalEvaluator:
    def __init__(
        self,
        chunker: Chunker,
        retriever: Retriever,
        query_strategy: QueryStrategy | None = None,
        reranker: Reranker | None = None,
        seed: int = 42,
    ):
        self.chunker = chunker
        self.retriever = retriever
        self.query_strategy = query_strategy
        self.reranker = reranker or None
        self.seed = seed
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
        config: dict | None = None,
    ) -> dict[str, Any]:
        final_k = final_k or top_k
        query_results = []

        # Accumulators for all doc-level metrics
        metric_keys = (
            [f"recall@{k}" for k in ks]
            + [f"precision@{k}" for k in ks]
            + [f"ndcg@{k}" for k in ks]
            + [f"f1@{k}" for k in ks]
        )
        total_doc = {k: 0.0 for k in metric_keys}
        total_doc["mrr"] = 0.0
        total_doc["map"] = 0.0

        total_snippet = {f"snippet_recall@{k}": 0.0 for k in ks}
        total_snippet |= {f"snippet_precision@{k}": 0.0 for k in ks}
        n_snippet_queries = 0

        start = time.perf_counter()
        n_queries = len(queries)
        for qi, query in enumerate(queries):
            if n_queries > 10 and qi % 50 == 0:
                elapsed = time.perf_counter() - start
                if qi > 0:
                    rate = qi / elapsed
                    eta = (n_queries - qi) / rate
                    print(
                        f"  [{qi}/{n_queries}] {elapsed:.1f}s elapsed, "
                        f"{rate:.1f} q/s, ETA {eta:.0f}s",
                        flush=True,
                    )
                else:
                    print(f"  [{qi}/{n_queries}] starting...", flush=True)

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
                for k in metric_keys:
                    total_doc[k] += doc_metrics[k]
                total_doc["mrr"] += doc_metrics["mrr"]
                total_doc["map"] += doc_metrics["map"]

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

        repro = _reproducibility_meta(config, self.seed)

        aggregated: dict[str, Any] = {
            "experiment_id": repro["experiment_id"],
            "timestamp": repro["timestamp"],
            "git_commit": repro["git_commit"],
            "seed": repro["seed"],
            "config_hash": repro["config_hash"],
            "python_version": repro["python_version"],
            "platform": repro["platform"],
            "n_queries": len(queries),
            "top_k": top_k,
            "final_k": final_k,
            "eval_mode": eval_mode,
            "latency_seconds": latency,
            "index_stats": {"n_chunks": len(self.items)},
        }

        if eval_mode in ("document", "both"):
            aggregated["metrics"] = {k: v / n for k, v in total_doc.items()}

        if eval_mode in ("snippet", "both"):
            ns = n_snippet_queries if n_snippet_queries else 1
            aggregated["snippet_metrics"] = {k: v / ns for k, v in total_snippet.items()}
            aggregated["n_snippet_queries"] = n_snippet_queries

        aggregated["per_query"] = query_results
        return aggregated
