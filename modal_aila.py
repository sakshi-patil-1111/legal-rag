"""AILA-2019 dense-leg evaluation on Modal (Qwen3-0.6B and 4B).

Runs both embedders sequentially in one A10G container, freeing the
model between runs so the 4B weights never share memory with the
0.6B. Dataset is fetched from Zenodo inside the container; outputs
(metrics + top-100 rank lists per task per model) land on the
legal-rag-results volume.

Usage:
    modal run modal_aila.py
    modal volume get legal-rag-results aila_statutes_dense_0.6b_metrics.json
"""

import json

import modal

app = modal.App("legal-rag-aila-dense")

results_vol = modal.Volume.from_name("legal-rag-results",
                                     create_if_missing=True)
hf_vol = modal.Volume.from_name("legal-rag-hf", create_if_missing=True)

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("torch", "sentence-transformers>=3.0", "numpy")
)

MODELS = ["Qwen/Qwen3-Embedding-0.6B", "Qwen/Qwen3-Embedding-4B"]


@app.function(image=image, gpu="A10G", timeout=7200,
              volumes={"/vol/results": results_vol, "/vol/hf": hf_vol},
              env={"HF_HOME": "/vol/hf"})
def run_all() -> None:
    import gc
    import urllib.request
    import zipfile
    from pathlib import Path

    import numpy as np
    import torch
    from sentence_transformers import SentenceTransformer

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

    tasks = {
        "precedents": (docs("Object_casedocs"),
                       qrels("relevance_judgments_priorcases.txt")),
        "statutes": (docs("Object_statutes", statutes=True),
                     qrels("relevance_judgments_statutes.txt")),
    }

    instr = ("Instruct: Given a legal query, retrieve relevant passages "
             "that answer the query\nQuery: ")
    KS = (1, 2, 3, 5, 10, 20, 50, 100)

    for model_name in MODELS:
        tag = model_name.split("-")[-1].lower()
        try:
            m = SentenceTransformer(
                model_name, device="cuda",
                model_kwargs={"torch_dtype": "float16"})
            # AILA judgments avg ~4.3k tokens; 8k cap keeps the causal
            # mask small enough that batch 8 never OOMs even on the
            # longest outliers.
            m.max_seq_length = 8192
            for task, (d, rels) in tasks.items():
                base = f"/vol/results/aila_{task}_dense_{tag}"
                if Path(base + "_metrics.json").exists():
                    print(f"skip {task} {model_name} (done)", flush=True)
                    continue
                labels = {q: ids & set(d) for q, ids in rels.items()
                          if q in queries}
                ids_list = sorted(d)
                texts = [d[i] for i in ids_list]
                print(f"{task} {model_name}: {len(d)} docs, "
                      f"{len(labels)} queries", flush=True)
                emb = m.encode(texts, normalize_embeddings=True,
                               batch_size=8, show_progress_bar=True)
                qemb = m.encode(
                    [instr + queries[q] for q in sorted(labels)],
                    normalize_embeddings=True, batch_size=8,
                    show_progress_bar=True)
                sims = qemb @ emb.T
                qids = sorted(labels)
                top100 = {q: [ids_list[j]
                              for j in np.argsort(-sims[i])[:100]]
                          for i, q in enumerate(qids)}
                rel_total = sum(len(v) for v in labels.values())
                by_k = []
                for k in KS:
                    tp = ap = mrr = 0.0
                    for q in qids:
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
                    f1 = (2 * prec * rec / (prec + rec)
                          if prec + rec else 0.0)
                    by_k.append({
                        "k": k, "p": round(prec * 100, 2),
                        "r": round(rec * 100, 2),
                        "f1": round(f1 * 100, 2),
                        "map": round(ap / len(labels) * 100, 2),
                        "mrr": round(mrr / len(labels) * 100, 2)})
                out = {"model": model_name, "task": task,
                       "dataset": "AILA-2019 (FIRE 2019)",
                       "n_docs": len(ids_list),
                       "n_queries": len(labels), "by_k": by_k}
                base = f"/vol/results/aila_{task}_dense_{tag}"
                with open(base + "_metrics.json", "w") as f:
                    json.dump(out, f, indent=2)
                with open(base + "_top100.json", "w") as f:
                    json.dump(top100, f)
                results_vol.commit()
                print(f"  R@100={by_k[-1]['r']} MAP={by_k[-1]['map']} "
                      f"MRR={by_k[-1]['mrr']}", flush=True)
        except Exception as e:  # keep going; other model may succeed
            print(f"FAILED {model_name}: {e}", flush=True)
        finally:
            try:
                del m
            except UnboundLocalError:
                pass
            gc.collect()
            torch.cuda.empty_cache()
    print("DONE")


@app.local_entrypoint()
def main() -> None:
    run_all.remote()
