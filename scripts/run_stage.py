"""Run a stage of the ablation study across multiple configs.

Usage:
  python scripts/run_stage.py stage_a    # runs all configs/stage_a_*.json
  python scripts/run_stage.py stage_b    # runs all configs/stage_b_*.json
  python scripts/run_stage.py stage_a --dry-run  # list configs without running

Each stage runs multiple configs through the Phase 1 pipeline (IL-PCSR)
and writes results to results/stage_{x}/.
"""

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


def run_config(config_path: Path) -> dict:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    output_dir = project_root / config["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)

    summary = []
    for task in config["dataset"]["tasks"]:
        data_root = project_root / config["dataset"].get("data_root", "data/fixtures/il_pcsr")
        queries, docs = load_il_pcsr(data_root, config["dataset"]["split"], task)

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
        results = evaluator.evaluate(
            queries,
            top_k=config["retrieval"]["top_k"],
            final_k=config.get("reranker", {}).get("final_k") or config["retrieval"]["top_k"],
            ks=tuple(config["evaluation"]["ks"]),
            config=config,
        )
        results["task"] = task
        results["experiment_name"] = config["experiment_name"]
        results["index_stats"] = index_stats
        results["indexing_latency"] = time.perf_counter() - start

        out_path = output_dir / f"{config['experiment_name']}_{task}.json"
        save_results(out_path, results)

        summary.append({
            "task": task,
            "experiment_name": config["experiment_name"],
            "metrics": results["metrics"],
            "latency_seconds": results["latency_seconds"],
            "output": str(out_path),
        })

        print(f"  [{config['experiment_name']}] Task: {task}")
        for k, v in results["metrics"].items():
            print(f"    {k}: {v:.4f}")

    return {"configs": summary}


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python scripts/run_stage.py <stage_name> [--dry-run]")
        print("Stages: stage_a, stage_b, stage_c, stage_d, stage_e")
        sys.exit(1)

    stage = sys.argv[1]
    dry_run = "--dry-run" in sys.argv

    config_dir = project_root / "configs"
    config_files = sorted(config_dir.glob(f"{stage}_*.json"))

    if not config_files:
        print(f"No configs found for {stage} in {config_dir}/")
        print(f"Expected files matching: {stage}_*.json")
        sys.exit(1)

    print(f"Stage: {stage}")
    print(f"Configs: {len(config_files)}")
    for cf in config_files:
        print(f"  - {cf.name}")

    if dry_run:
        print("\n--dry-run: not executing")
        return

    print()
    all_results = []
    for cf in config_files:
        print(f"Running: {cf.name}")
        result = run_config(cf)
        all_results.append({"config_file": cf.name, **result})

    # Write stage summary
    output_dir = project_root / "results" / stage
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / "stage_summary.json"
    save_results(summary_path, {"stage": stage, "results": all_results})
    print(f"\nStage summary written to: {summary_path}")


if __name__ == "__main__":
    main()
