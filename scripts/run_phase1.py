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


def run_task(config: dict, task: str) -> dict:
    data_root = project_root / config["dataset"].get("data_root", "data/fixtures/il_pcsr")
    queries, docs = load_il_pcsr(data_root, config["dataset"]["split"], task)

    chunker = build_chunker(**config["chunking"])
    retriever = build_retriever(config["retrieval"])
    query_strategy = build_query_strategy(config["query"]["strategy"])
    reranker = build_reranker(config.get("reranker"))

    evaluator = RetrievalEvaluator(
        chunker=chunker,
        retriever=retriever,
        query_strategy=query_strategy,
        reranker=reranker,
    )

    start = time.perf_counter()
    index_stats = evaluator.index(docs)
    eval_results = evaluator.evaluate(
        queries,
        top_k=config["retrieval"]["top_k"],
        final_k=config.get("reranker", {}).get("final_k") or config["retrieval"]["top_k"],
        ks=tuple(config["evaluation"]["ks"]),
    )
    eval_results["task"] = task
    eval_results["experiment_name"] = config["experiment_name"]
    eval_results["index_stats"] = index_stats
    eval_results["config"] = config
    eval_results["indexing_latency"] = time.perf_counter() - start
    return eval_results


def main() -> None:
    config_name = sys.argv[1] if len(sys.argv) > 1 else "phase1_fixture.json"
    config_path = project_root / "configs" / config_name
    config = json.loads(config_path.read_text(encoding="utf-8"))
    output_dir = project_root / config["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)

    summary = []
    for task in config["dataset"]["tasks"]:
        results = run_task(config, task)
        out_path = output_dir / f"phase1_{task}.json"
        save_results(out_path, results)
        summary.append({
            "task": task,
            "metrics": results["metrics"],
            "output": str(out_path),
        })
        print(f"Task: {task}")
        for k, v in results["metrics"].items():
            print(f"  {k}: {v:.4f}")

    summary_path = output_dir / "phase1_summary.json"
    save_results(summary_path, {
        "experiment_name": config["experiment_name"],
        "tasks": summary,
    })
    print(f"Summary written to: {summary_path}")


if __name__ == "__main__":
    main()
