"""
End-to-end latency benchmark for the PRODUCTION streaming path (trigger_pipeline_stream).

Measures what the user actually feels:
  - t_first_token: time until the first answer chunk streams (perceived latency)
  - t_complete   : time until the full answer + citations are done

Uses real Gemini calls (flash models only). Run:
  TORCH_NUM_THREADS=4 .venv/Scripts/python.exe -u scripts/bench_e2e.py
"""
import os, sys, time, json
_HERE = os.path.dirname(os.path.abspath(__file__)); _BACKEND = os.path.dirname(_HERE)
os.chdir(_BACKEND); sys.path.insert(0, _BACKEND)

import torch
torch.set_num_threads(int(os.environ.get("TORCH_NUM_THREADS", "4")))

from app.knowledge.embeddings import embedding_service
from app.knowledge.bm25_manager import bm25_manager
from app.ai.orchestrator import rag_orchestrator

# Representative complex queries (CIVIC forces the multi-query streaming path).
QUERIES = [
    "What are the conditions for granting anticipatory bail?",
    "I paid 80 lakh to a builder for a flat in 2019. Possession was promised in 2022. "
    "Builder claims force majeure. I want a full refund with interest. What are my rights?",
    "I bought a defective product. Under the Consumer Protection Act, what rights do I have "
    "and which commission should I approach?",
]

def time_stream(question, task_type="CIVIC"):
    filters = {"tenant_id": "global"}
    t0 = time.time()
    t_first = None
    n_chunks = 0
    chars = 0
    metrics = {}
    for event in rag_orchestrator.trigger_pipeline_stream(question, filters, [], task_type=task_type):
        if not event.startswith("data: "):
            continue
        try:
            data = json.loads(event[6:])
        except Exception:
            continue
        if data.get("type") == "chunk":
            if t_first is None:
                t_first = time.time() - t0
            n_chunks += 1
            chars += len(data.get("data", ""))
        elif data.get("type") == "complete":
            metrics = data.get("metrics", {}) or {}
        elif data.get("type") == "error":
            return {"error": data.get("data"), "t_total": round(time.time() - t0, 2),
                    "metrics": metrics}
    t_total = time.time() - t0
    return {"t_first_token": round(t_first, 2) if t_first else None,
            "t_complete": round(t_total, 2), "chunks": n_chunks, "chars": chars,
            "metrics": metrics}

def fmt_metrics(m):
    if not m:
        return ""
    return (f"emb={m.get('embedding_time', 0)} ret={m.get('retrieval_time', 0)} "
            f"prompt={m.get('prompt_construction_time', 0)} ttft={m.get('ttft', 0)} "
            f"gen={m.get('model_processing_time', 0)} out_tok~{m.get('output_tokens', 0)}")

def main():
    print("Warming models + BM25 + Chroma + reranker...", flush=True)
    bm25_manager.get_index("global")
    _warm_emb = embedding_service.embed_query("warmup")
    # A full hybrid search warms the Chroma collections AND loads the
    # cross-encoder, which otherwise lands on the first real request (~15s).
    from app.knowledge.hybrid_retriever import hybrid_retriever
    _ = hybrid_retriever.search("warmup legal query", _warm_emb, n_results=5, predicted_domains={})
    print("warmed.\n", flush=True)

    rows = []
    for q in QUERIES:
        r = time_stream(q)
        r["q"] = q[:55]
        rows.append(r)
        if "error" in r:
            print(f"ERROR  {r['t_total']:5.2f}s  {r['q']}  -> {r['error'][:60]}", flush=True)
        else:
            print(f"complete={r['t_complete']:6.2f}s chunks={r['chunks']:3d} chars={r['chars']:5d} | {r['q']}", flush=True)
        print(f"        stages: {fmt_metrics(r.get('metrics'))}", flush=True)

    ok = [r for r in rows if "error" not in r]
    if ok:
        avg_complete = sum(r["t_complete"] for r in ok) / len(ok)
        avg_gen = sum(r.get("metrics", {}).get("model_processing_time", 0) for r in ok) / len(ok)
        avg_ret = sum(r.get("metrics", {}).get("retrieval_time", 0) for r in ok) / len(ok)
        print(f"\nAVG complete: {avg_complete:.2f}s  (retrieval {avg_ret:.2f}s, generation {avg_gen:.2f}s)", flush=True)
    with open(os.path.join("scripts", "e2e_metrics.json"), "w") as f:
        json.dump(rows, f, indent=2)
    print("wrote scripts/e2e_metrics.json", flush=True)

if __name__ == "__main__":
    main()
