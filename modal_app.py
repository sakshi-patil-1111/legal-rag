"""Modal runner for IL-PCSR GPU experiments.

Usage:
    modal run modal_app.py                # launch all RUNS in parallel, wait, print tails
    modal run modal_app.py --configs '[["stage_b2b_qwen3_pcr.json","T4"]]'

Volumes:
    legal-rag-data    -> /vol/data/il_pcsr/{queries,statutes,precedents}.json (+ /vol/data/cache)
    legal-rag-results -> results land here under the config's output_dir
    legal-rag-hf      -> HF_HOME cache so model downloads persist across runs
"""

import modal

app = modal.App("legal-rag-experiments")

data_vol = modal.Volume.from_name("legal-rag-data")
results_vol = modal.Volume.from_name("legal-rag-results", create_if_missing=True)
hf_vol = modal.Volume.from_name("legal-rag-hf", create_if_missing=True)

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "numpy>=1.24",
        "scikit-learn>=1.3",
        "bm25s>=0.2",
        "torch",
        "sentence-transformers>=3.0",
        "tqdm",
        "python-dotenv",
        "datasets",
    )
    .add_local_dir("src", remote_path="/app/src")
    .add_local_dir("scripts", remote_path="/app/scripts")
    .add_local_dir("configs", remote_path="/app/configs")
)

RUNS = [
    ("stage_b2b_qwen3_pcr.json", "A10G"),            # Qwen3-0.6B dense, PCR only
    ("stage_c2_hybrid_ngram_qwen3.json", "A10G"),    # ngram5 BM25 + Qwen3-0.6B RRF, both tasks
    ("stage_b3_qwen3_4b.json", "A10G"),              # Qwen3-4B dense, both tasks
    ("stage_c3_hybrid_ngram_qwen3_4b.json", "A10G"), # ngram5 BM25 + Qwen3-4B RRF, both tasks
    ("stage_d2_hybrid_ce_rerank.json", "A10G"),      # hybrid top-50 + bge-reranker-v2-m3 -> 10
    ("stage_d3_hybrid_llm_rerank.json", "A10G"),     # hybrid top-50 + gpt-5-mini listwise -> 10
]


@app.function(
    image=image,
    volumes={"/vol/data": data_vol},
    secrets=[modal.Secret.from_name("legal-rag-hf")],
    timeout=3600,
)
def bootstrap_data() -> str:
    """Download IL-PCSR from HF into the shared volume (needs gated HF_TOKEN)."""
    import os
    import subprocess
    import sys

    os.makedirs("/vol/data", exist_ok=True)
    proc = subprocess.run(
        [sys.executable, "scripts/download_il_pcsr.py"],
        cwd="/app",
        env={**os.environ, "HF_TOKEN": os.environ["HF_TOKEN"]},
        capture_output=True,
        text=True,
    )
    print(proc.stdout[-4000:])
    print(proc.stderr[-2000:], file=sys.stderr)
    if proc.returncode != 0:
        raise RuntimeError(f"download failed: {proc.stderr[-1000:]}")
    # Move from the project data dir into the volume layout.
    import shutil
    src = "/app/data/raw/il_pcsr"
    dst = "/vol/data/il_pcsr"
    os.makedirs(dst, exist_ok=True)
    for name in ("queries.json", "statutes.json", "precedents.json"):
        shutil.copy2(f"{src}/{name}", f"{dst}/{name}")
    data_vol.commit()
    return proc.stdout[-500:]


@app.function(
    image=image,
    gpu="A10G",
    volumes={"/vol/data": data_vol, "/vol/out": results_vol, "/vol/hf": hf_vol},
    env={"HF_HOME": "/vol/hf/hub"},
    secrets=[modal.Secret.from_name("legal-rag-openai")],
    timeout=6 * 3600,
)
def run_experiment(config_name: str) -> dict:
    import json
    import os
    import subprocess
    import sys

    # Reconstruct the on-disk layout the configs expect:
    #   data/raw/il_pcsr/*.json, data/cache/, results/
    os.makedirs("/app/data/raw", exist_ok=True)
    if not os.path.exists("/app/data/raw/il_pcsr"):
        os.symlink("/vol/data/il_pcsr", "/app/data/raw/il_pcsr")
    os.makedirs("/vol/data/cache", exist_ok=True)
    if not os.path.exists("/app/data/cache"):
        os.symlink("/vol/data/cache", "/app/data/cache")
    if not os.path.exists("/app/results"):
        os.symlink("/vol/out", "/app/results")

    proc = subprocess.run(
        [sys.executable, "scripts/run_phase1.py", config_name],
        cwd="/app",
        capture_output=True,
        text=True,
    )
    print(proc.stdout[-8000:])
    if proc.stderr:
        print(proc.stderr[-4000:], file=sys.stderr)
    data_vol.commit()
    results_vol.commit()
    hf_vol.commit()
    if proc.returncode != 0:
        raise RuntimeError(f"{config_name} failed rc={proc.returncode}: {proc.stderr[-2000:]}")
    return {"config": config_name, "tail": proc.stdout[-3000:]}


@app.local_entrypoint()
def main(configs: str = ""):
    import json as _json

    runs = _json.loads(configs) if configs else RUNS
    calls = [
        (cfg, run_experiment.with_options(gpu=gpu).spawn(cfg)) for cfg, gpu in runs
    ]
    print(f"spawned {len(calls)} runs: {[c for c, _ in calls]}")
    for cfg, call in calls:
        try:
            res = call.get()
            print(f"[DONE] {cfg}\n{res['tail'][-1500:]}")
        except Exception as e:  # noqa: BLE001
            print(f"[FAIL] {cfg}: {e}")
