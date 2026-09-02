import time
from pathlib import Path
from typing import Any

from .bm25 import SimpleBM25
from .corpus import load_fixture
from .metrics import evaluate_query
from .schemas import LegalDocument, LegalQuery
from .tokenization import tokenize


def run_bm25_experiment(
    fixture_path: Path,
    top_k: int = 10,
    ks: tuple[int, ...] = (1, 3, 5, 10),
) -> dict[str, Any]:
    documents, queries = load_fixture(fixture_path)
    index = SimpleBM25(documents, tokenize)

    query_results = []
    total_recall = {f"recall@{k}": 0.0 for k in ks}
    total_mrr = 0.0
    start = time.perf_counter()

    for query in queries:
        predictions = index.retrieve(query.text, top_k=top_k)
        metrics = evaluate_query(predictions, query.ground_truth, ks=ks)
        for k in ks:
            total_recall[f"recall@{k}"] += metrics[f"recall@{k}"]
        total_mrr += metrics["mrr"]

        query_results.append({
            "qid": query.qid,
            "text": query.text,
            "predictions": predictions,
            "ground_truth": query.ground_truth,
            "metrics": metrics,
        })

    latency = time.perf_counter() - start
    n = len(queries) if queries else 1

    return {
        "experiment": "phase0_bm25_fixture",
        "n_queries": len(queries),
        "top_k": top_k,
        "latency_seconds": latency,
        "metrics": {k: v / n for k, v in total_recall.items()}
        | {"mrr": total_mrr / n},
        "per_query": query_results,
    }
