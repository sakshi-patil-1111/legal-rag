import json
import sys
import time
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from legal_rag.corpus import save_results
from legal_rag.datasets import load_legalbench_rag
from legal_rag.evaluator import RetrievalEvaluator
from legal_rag.factory import build_chunker, build_query_strategy, build_reranker, build_retriever


def main() -> None:
    config_path = project_root / "configs" / "phase2_fixture.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    data_root = project_root / "data" / "fixtures" / "legalbench_rag"

    queries, docs = load_legalbench_rag(data_root, config["dataset"]["split"])

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
    top_k = config["retrieval"]["top_k"]
    final_k = config.get("reranker", {}).get("final_k") or top_k
    results = evaluator.evaluate(
        queries,
        top_k=top_k,
        final_k=final_k,
        ks=tuple(config["evaluation"]["ks"]),
    )
    results["experiment_name"] = config["experiment_name"]
    results["config"] = config
    results["index_stats"] = index_stats
    results["indexing_latency"] = time.perf_counter() - start

    output_dir = project_root / config["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "phase2_legalbench_rag.json"
    save_results(output_path, results)

    print(f"Experiment: {results['experiment_name']}")
    print(f"Queries: {results['n_queries']}")
    print(f"Chunks: {results['index_stats']['n_chunks']}")
    print("Metrics:")
    for k, v in results["metrics"].items():
        print(f"  {k}: {v:.4f}")
    print(f"Results written to: {output_path}")


if __name__ == "__main__":
    main()
