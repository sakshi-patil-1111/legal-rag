import csv
import itertools
import json
import sys
import time
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from legal_rag.corpus import save_results
from legal_rag.datasets import load_il_pcsr
from legal_rag.evaluator import RetrievalEvaluator
from legal_rag.factory import build_chunker, build_query_strategy, build_reranker, build_retriever


GRID = {
    "chunking": [
        {"strategy": "whole"},
        {"strategy": "fixed_token", "size": 100, "overlap": 0},
        {"strategy": "fixed_char", "size": 300, "overlap": 0},
        {"strategy": "recursive", "size": 100, "overlap": 0},
    ],
    "retrieval": [
        {"type": "bm25", "top_k": 10},
        {"type": "dense", "top_k": 10, "n_components": 2},
        {"type": "hybrid", "top_k": 10, "dense_n_components": 2},
    ],
    "query": [
        "direct",
        "keyword",
        "hyde",
    ],
    "reranker": [
        None,
        {"enabled": True, "type": "token_overlap", "final_k": 3},
    ],
}


def run_combo(base_config: dict, task: str, combo: dict) -> dict:
    data_root = project_root / "data" / "fixtures" / "il_pcsr"
    queries, docs = load_il_pcsr(data_root, base_config["dataset"]["split"], task)

    chunker = build_chunker(**combo["chunking"])
    retriever = build_retriever(combo["retrieval"])
    query_strategy = build_query_strategy(combo["query"])
    reranker = build_reranker(combo["reranker"])

    evaluator = RetrievalEvaluator(
        chunker=chunker,
        retriever=retriever,
        query_strategy=query_strategy,
        reranker=reranker,
    )

    start = time.perf_counter()
    index_stats = evaluator.index(docs)
    top_k = combo["retrieval"]["top_k"]
    final_k = (combo["reranker"] or {}).get("final_k") or top_k
    results = evaluator.evaluate(
        queries,
        top_k=top_k,
        final_k=final_k,
        ks=tuple(base_config["evaluation"]["ks"]),
    )

    return {
        "task": task,
        "chunking": combo["chunking"]["strategy"],
        "retrieval": combo["retrieval"]["type"],
        "query": combo["query"],
        "reranker": combo["reranker"]["type"] if combo["reranker"] else "none",
        "n_queries": results["n_queries"],
        "n_chunks": index_stats["n_chunks"],
        **results["metrics"],
        "latency_seconds": time.perf_counter() - start,
    }


def main() -> None:
    config_path = project_root / "configs" / "phase1_fixture.json"
    base_config = json.loads(config_path.read_text(encoding="utf-8"))
    output_dir = project_root / base_config["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)

    keys = list(GRID)
    values = [GRID[k] for k in keys]
    rows = []

    for task in base_config["dataset"]["tasks"]:
        for combo_values in itertools.product(*values):
            combo = dict(zip(keys, combo_values))
            row = run_combo(base_config, task, combo)
            rows.append(row)
            print(
                f"task={row['task']} | chunk={row['chunking']} | ret={row['retrieval']} | "
                f"q={row['query']} | rerank={row['reranker']} | MRR={row['mrr']:.4f}"
            )

    rows.sort(key=lambda r: (r["task"], -r["mrr"]))

    csv_path = output_dir / "comparison_grid.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    summary = {}
    for task in base_config["dataset"]["tasks"]:
        task_rows = [r for r in rows if r["task"] == task]
        summary[task] = {
            "best_mrr": task_rows[0],
            "best_recall@3": max(task_rows, key=lambda r: r["recall@3"]),
        }

    json_path = output_dir / "comparison_grid_summary.json"
    save_results(json_path, summary)

    print(f"\nComparison table written to: {csv_path}")
    print(f"Summary written to: {json_path}")
    print("\nBest by MRR per task:")
    for task, best in summary.items():
        r = best["best_mrr"]
        print(
            f"  {task}: chunk={r['chunking']}, ret={r['retrieval']}, "
            f"q={r['query']}, rerank={r['reranker']}, MRR={r['mrr']:.4f}"
        )


if __name__ == "__main__":
    main()
