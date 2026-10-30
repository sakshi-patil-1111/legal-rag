import os
import subprocess
import sys

os.makedirs("/kaggle/working/legal-rag", exist_ok=True)
subprocess.run(
    ["git", "clone", "--depth", "1", "-b", "neel",
     "https://github.com/sakshi-patil-1111/legal-rag.git",
     "/kaggle/working/legal-rag"],
    check=True,
)

import glob

data_dir = "/kaggle/working/legal-rag/data/raw/il_pcsr"
os.makedirs(data_dir, exist_ok=True)
found = []
for f in ("queries.json", "statutes.json", "precedents.json"):
    hits = glob.glob(f"/kaggle/input/**/{f}", recursive=True)
    if not hits:
        raise FileNotFoundError(
            f"{f} not under /kaggle/input; have: "
            + str(glob.glob("/kaggle/input/**/*", recursive=True)[:50])
        )
    dst = f"{data_dir}/{f}"
    if not os.path.exists(dst):
        os.symlink(hits[0], dst)
    found.append(hits[0])
print("linked:", found)

subprocess.run(
    [sys.executable, "-m", "pip", "install", "-q", "-U",
     "sentence-transformers>=3.0", "datasets", "accelerate"],
    check=True,
)

subprocess.run(
    [sys.executable, "scripts/finetune_embedder.py",
     "--model", "Qwen/Qwen3-Embedding-0.6B",
     "--epochs", "1", "--batch", "4",
     "--out", "/kaggle/working/ft_out"],
    cwd="/kaggle/working/legal-rag",
    check=True,
)
print("DONE")
