import json
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from legal_rag.corpus import save_results
from legal_rag.experiment import run_bm25_experiment


def main() -> None:
    config_path = project_root / "configs" / "phase0_fixture.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    fixture_path = project_root / config["fixture"]
    top_k = config["retriever"]["top_k"]
    ks = tuple(config["evaluation"]["ks"])
    output_path = project_root / config["evaluation"]["output_path"]

    results = run_bm25_experiment(fixture_path, top_k=top_k, ks=ks)
    save_results(output_path, results)

    print(f"Experiment: {results['experiment']}")
    print(f"Queries: {results['n_queries']}")
    print(f"Latency: {results['latency_seconds']:.6f}s")
    print("Metrics:")
    for metric, value in results["metrics"].items():
        print(f"  {metric}: {value:.4f}")
    print(f"Results written to: {output_path}")


if __name__ == "__main__":
    main()
