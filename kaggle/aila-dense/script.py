import json
import os
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

subprocess.run(
    [sys.executable, "-m", "pip", "install", "-q", "-U",
     "sentence-transformers>=3.0", "datasets"],
    check=True,
)

import numpy as np  # noqa: E402
from sentence_transformers import SentenceTransformer  # noqa: E402

# --- fetch AILA-2019 from Zenodo ---
url = ("https://zenodo.org/api/records/4063986/files/"
       "AILA_2019_dataset.zip/content")
urllib.request.urlretrieve(url, "/tmp/aila.zip")
with zipfile.ZipFile("/tmp/aila.zip") as z:
    z.extractall("/tmp/aila")
root = Path("/tmp/aila")

queries = {}
for line in (root / "Query_doc.txt").read_text().splitlines():
    if "||" in line:
        qid, text = line.split("||", 1)
        queries[qid.strip()] = text.strip()


def qrels(p):
    out = {}
    for line in (root / p).read_text().splitlines():
        parts = line.split()
        if len(parts) >= 4 and int(parts[3]) >= 1:
            out.setdefault(parts[0], set()).add(parts[2])
    return out


def docs(d, statutes=False):
    out = {}
    for f in sorted((root / d).iterdir()):
        if statutes:
            raw = f.read_text(errors="replace").splitlines()
            text = " ".join(
                l.split(":", 1)[1].strip() if ":" in l else l
                for l in raw)
        else:
            text = f.read_text(errors="replace")
        out[f.stem] = text
    return out


m = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B", device="cuda",
                        model_kwargs={"torch_dtype": "float16"})
INSTR = ("Instruct: Given a legal query, retrieve relevant passages "
         "that answer the query\nQuery: ")
KS = (1, 2, 3, 5, 10, 20, 50, 100)


def evaluate(ranks, labels, rel_total):
    by_k = []
    for k in KS:
        tp = sum(len(set(r[:k]) & ids)
                 for r, ids in zip(ranks.values(), labels.values()))
        prec = tp / (len(labels) * k)
        rec = tp / rel_total
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        ap = mrr = 0.0
        for qid, ids in labels.items():
            rr = 0.0
            for i, h in enumerate(ranks[qid][:k], 1):
                if h in ids:
                    rr = 1.0 / i
                    break
            mrr += rr
            hits = [1 if h in ids else 0 for h in ranks[qid][:k]]
            if any(hits):
                ap += sum(sum(hits[:i + 1]) / (i + 1)
                          for i, x in enumerate(hits) if x) / len(ids)
        by_k.append({"k": k, "p": round(prec * 100, 2),
                     "r": round(rec * 100, 2),
                     "f1": round(f1 * 100, 2),
                     "map": round(ap / len(labels) * 100, 2),
                     "mrr": round(mrr / len(labels) * 100, 2)})
    return by_k


def run(task, doc_dir, rels_file, statutes):
    d = docs(doc_dir, statutes)
    labels = {q: ids & set(d) for q, ids in qrels(rels_file).items()
              if q in queries}
    ids_list = sorted(d)
    texts = [d[i] for i in ids_list]
    print(f"{task}: {len(d)} docs, {len(labels)} queries", flush=True)
    emb = m.encode(texts, normalize_embeddings=True, batch_size=4,
                   show_progress_bar=True)
    qemb = m.encode([queries[q] for q in sorted(labels)],
                    normalize_embeddings=True, batch_size=8,
                    prompt=INSTR, show_progress_bar=True)
    sims = qemb @ emb.T
    ranks = {}
    for qi, qid in enumerate(sorted(labels)):
        top = np.argsort(-sims[qi])[:100]
        ranks[qid] = [ids_list[i] for i in top]
    by_k = evaluate(ranks, labels, sum(len(v) for v in labels.values()))
    b = by_k[-1]
    print(f"  dense R@100={b['r']} MAP={b['map']} MRR={b['mrr']}",
          flush=True)
    return {"by_k": by_k, "ranks": ranks}


out = {
    "precedents": run("precedents", "Object_casedocs",
                      "relevance_judgments_priorcases.txt", False),
    "statutes": run("statutes", "Object_statutes",
                    "relevance_judgments_statutes.txt", True),
}
out["model"] = "Qwen/Qwen3-Embedding-0.6B"
out["dataset"] = "AILA-2019 (FIRE 2019), Zenodo 4063986"
json.dump({k: {"by_k": v["by_k"]} for k, v in out.items()
           if k != "precedents" or True},
          open("/kaggle/working/aila_dense_metrics.json", "w"),
          indent=2)
json.dump({t: v["ranks"] for t, v in
           (("precedents", out["precedents"]),
            ("statutes", out["statutes"]))},
          open("/kaggle/working/aila_dense_top100.json", "w"))
print("done", flush=True)
