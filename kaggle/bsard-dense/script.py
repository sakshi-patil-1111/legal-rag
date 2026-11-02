import json
import subprocess
import sys

subprocess.run(
    [sys.executable, "-m", "pip", "install", "-q", "-U",
     "sentence-transformers>=3.0", "datasets"],
    check=True,
)

import numpy as np  # noqa: E402
from datasets import load_dataset  # noqa: E402
from sentence_transformers import SentenceTransformer  # noqa: E402

corpus = load_dataset("maastrichtlawtech/bsard", "corpus", split="corpus")
qs = load_dataset("maastrichtlawtech/bsard", "questions", split="test")

docs = sorted(corpus, key=lambda r: r["id"])
ids = [str(r["id"]) for r in docs]
texts = [
    (f"{r['description']}\n{r['article']}" if r.get("description")
     else r["article"]) or ""
    for r in docs
]
labels = {
    str(r["id"]): [s.strip() for s in str(r["article_ids"]).split(",")
                   if s.strip()]
    for r in qs
}
queries = {str(r["id"]): r["question"] for r in qs}
print(f"{len(ids)} articles, {len(labels)} queries", flush=True)

m = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B",
                        device="cuda",
                        model_kwargs={"torch_dtype": "float16"})
INSTR = ("Instruct: Given a legal query, retrieve relevant passages "
         "that answer the query\nQuery: ")

emb = m.encode(texts, normalize_embeddings=True, batch_size=16,
               show_progress_bar=True)
qemb = m.encode([INSTR + queries[q] for q in labels],
                normalize_embeddings=True, batch_size=16,
                show_progress_bar=True)

sims = qemb @ emb.T
top100 = {q: [ids[j] for j in np.argsort(-sims[i])[:100]]
          for i, q in enumerate(labels)}

rel_total = sum(len(v) for v in labels.values())
by_k = []
for k in (1, 2, 3, 5, 10, 20, 50, 100):
    tp = ap = mrr = 0.0
    for q in labels:
        lab = set(labels[q])
        hits = top100[q][:k]
        tp += len(set(hits) & lab)
        seen = apq = rr = 0.0
        for rank, h in enumerate(hits, 1):
            if h in lab:
                seen += 1
                apq += seen / rank
                if rr == 0:
                    rr = 1 / rank
        ap += apq / len(lab) if lab else 0.0
        mrr += rr
    prec = tp / (len(labels) * k)
    rec = tp / rel_total
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    by_k.append({"k": k, "p": round(prec * 100, 2),
                 "r": round(rec * 100, 2), "f1": round(f1 * 100, 2),
                 "map": round(ap / len(labels) * 100, 2),
                 "mrr": round(mrr / len(labels) * 100, 2)})

out = {"model": "Qwen/Qwen3-Embedding-0.6B",
       "dataset": "maastrichtlawtech/bsard questions/test",
       "n_docs": len(ids), "n_queries": len(labels),
       "context_prepend": True, "by_k": by_k}
json.dump(out, open("/kaggle/working/bsard_dense_metrics.json", "w"),
          indent=2)
json.dump(top100, open("/kaggle/working/bsard_dense_top100.json", "w"))
print(json.dumps(by_k, indent=1))
print("DONE")
