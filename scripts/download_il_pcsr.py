"""Download IL-PCSR from HuggingFace and save as local JSON.

Requires HF_TOKEN in environment (gated dataset).
Saves to data/raw/il_pcsr/ in the format the existing adapter expects:
  - queries.json   (with train_queries, dev_queries, test_queries keys)
  - statutes.json  (list of statute candidates)
  - precedents.json (list of precedent candidates)
"""
import json
import os
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from datasets import load_dataset

OUTPUT_DIR = project_root / "data" / "raw" / "il_pcsr"


def to_serializable(obj):
    """Convert HF dataset values to JSON-serializable types."""
    if isinstance(obj, list):
        return [to_serializable(v) for v in obj]
    if isinstance(obj, dict):
        return {k: to_serializable(v) for k, v in obj.items()}
    return obj


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # --- Queries ---
    print("Downloading queries config...")
    ds_queries = load_dataset("Exploration-Lab/IL-PCSR", name="queries")
    queries_data = {}
    for split_name in ["train_queries", "dev_queries", "test_queries"]:
        examples = []
        for ex in ds_queries[split_name]:
            examples.append(to_serializable(dict(ex)))
        queries_data[split_name] = examples
        print(f"  {split_name}: {len(examples)} queries")

    queries_path = OUTPUT_DIR / "queries.json"
    queries_path.write_text(json.dumps(queries_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  Saved to {queries_path}")

    # --- Statutes ---
    print("Downloading statutes config...")
    ds_statutes = load_dataset("Exploration-Lab/IL-PCSR", name="statutes")
    statutes = []
    for ex in ds_statutes["statute_candidates"]:
        statutes.append(to_serializable(dict(ex)))
    print(f"  statute_candidates: {len(statutes)} provisions")

    statutes_path = OUTPUT_DIR / "statutes.json"
    statutes_path.write_text(json.dumps(statutes, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  Saved to {statutes_path}")

    # --- Precedents ---
    print("Downloading precedents config...")
    ds_precedents = load_dataset("Exploration-Lab/IL-PCSR", name="precedents")
    precedents = []
    for ex in ds_precedents["precedent_candidates"]:
        precedents.append(to_serializable(dict(ex)))
    print(f"  precedent_candidates: {len(precedents)} judgments")

    precedents_path = OUTPUT_DIR / "precedents.json"
    precedents_path.write_text(json.dumps(precedents, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  Saved to {precedents_path}")

    print("\nDone. IL-PCSR data saved to", OUTPUT_DIR)


if __name__ == "__main__":
    main()
