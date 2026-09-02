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
    config_name = sys.argv[1] if len(sys.argv) > 1 else "phase2_fixture.json"
    config_path = project_root / "configs" / config_name
    config = json.loads(config_path.read_text(encoding="utf-8"))
    data_root = project_root / config["dataset"].get("data_root", "data/fixtures/legalbench_rag")
    benchmark = config["dataset"].get("benchmark")
    eval_mode = config.get("eval_mode", "both")

    queries, docs = load_legalbench_rag(data_root, config["dataset"]["split"], benchmark=benchmark)

    chunker = build_chunker(**config["chunking"])
    retriever = build_retriever(config["retrieval"])
    query_strategy = build_query_strategy(
        config["query"]["strategy"], **config.get("query", {}).get("params", {}),
    )
    reranker = build_reranker(config.get("reranker"))

    evaluator = RetrievalEvaluator(
        chunker=chunker,
        retriever=retriever,
        query_strategy=query_strategy,
        reranker=reranker,
        seed=config.get("seed", 42),
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
        eval_mode=eval_mode,
        config=config,
    )
    results["experiment_name"] = config["experiment_name"]
    results["config"] = config
    results["index_stats"] = index_stats
    results["indexing_latency"] = time.perf_counter() - start

    output_dir = project_root / config["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{config['experiment_name']}.json"
    save_results(output_path, results)

    print(f"Experiment: {results['experiment_name']}")
    print(f"Queries: {results['n_queries']}")
    print(f"Chunks: {results['index_stats']['n_chunks']}")
    print(f"Eval mode: {eval_mode}")
    if "metrics" in results:
        print("Document-level metrics:")
        for k, v in results["metrics"].items():
            print(f"  {k}: {v:.4f}")
    if "snippet_metrics" in results:
        print(f"Snippet queries: {results.get('n_snippet_queries', 0)}")
        print("Snippet-level metrics:")
        for k, v in results["snippet_metrics"].items():
            print(f"  {k}: {v:.4f}")
    print(f"Results written to: {output_path}")


if __name__ == "__main__":
    main()
