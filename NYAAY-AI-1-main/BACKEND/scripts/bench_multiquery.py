"""
Deterministic multi-query retrieval benchmark (NO Gemini API calls).

Feeds fixed sub-queries + domains straight into RAGOrchestrator._multi_query_retrieve,
so it isolates the embedding + fusion + rerank cost of the real retrieval fan-out
(the part that dominates end-to-end latency). Run before AND after the rerank-once
refactor to compare latency + SC representation.
"""
import os, sys, time, json
_HERE = os.path.dirname(os.path.abspath(__file__)); _BACKEND = os.path.dirname(_HERE)
os.chdir(_BACKEND); sys.path.insert(0, _BACKEND)

import torch
torch.set_num_threads(int(os.environ.get("TORCH_NUM_THREADS", "4")))

from app.knowledge.embeddings import embedding_service
from app.knowledge.bm25_manager import bm25_manager
from app.knowledge.hybrid_retriever import hybrid_retriever
from app.ai.orchestrator import rag_orchestrator

# (id, raw_question, sub_queries, domains, explicit_sc)
CASES = [
    ("T1_rape_consent",
     "My client was convicted for rape. The complainant delayed filing the FIR by 3 months, and there were no physical injuries. We have friendly WhatsApp chats showing consent. Are there Supreme Court judgments on this?",
     ["evidentiary value of delayed FIR in rape cases",
      "consent as defence in rape absence of physical injury",
      "Supreme Court precedent rape conviction WhatsApp chats consent"],
     {"Criminal Law": 0.9}, True),
    ("T3_homebuyer_rera",
     "I paid 80 lakh to a builder for a flat in 2019. Possession was promised in 2022. Builder claims force majeure. I want a full refund with interest. What does RERA say and are there Supreme Court judgments?",
     ["RERA refund with interest delayed possession",
      "force majeure defence builder real estate",
      "Supreme Court judgment homebuyer refund RERA"],
     {"Consumer Law": 0.8, "Property & Real Estate": 0.6}, True),
    ("S1_anticipatory_bail",
     "What are the conditions for granting anticipatory bail?",
     ["conditions for granting anticipatory bail",
      "anticipatory bail section BNSS CrPC"],
     {"Criminal Law": 0.9}, False),
    ("S4_consumer_defective",
     "I bought a defective product. Under the Consumer Protection Act, what rights do I have and which commission should I approach?",
     ["consumer rights defective product Consumer Protection Act",
      "consumer commission jurisdiction pecuniary limit"],
     {"Consumer & Product Liability": 0.9}, False),
]

def sc_count(chunks):
    n = 0
    for c in chunks:
        m = c.get("metadata", {})
        if m.get("court_level") == "Supreme Court" or m.get("document_type") == "judgment" \
           or "Supreme Court" in str(m.get("source_name", "")) or "SC_" in str(c.get("id", "")):
            n += 1
    return n

def main():
    print("Warming models + BM25...", flush=True)
    bm25_manager.get_index("global")
    _ = embedding_service.embed_query("warmup")
    # one full warm pass so the cross-encoder/torch threads are initialized
    _ = rag_orchestrator._multi_query_retrieve(
        ["warmup query"], embedding_service.embed_query("warmup query"),
        {}, "any", None, False)
    print("warmed.\n", flush=True)

    results = []
    for cid, question, subq, domains, sc in CASES:
        base_emb = embedding_service.embed_query(subq[0])

        # (a) Unseeded path == sync pipeline (trigger_pipeline).
        t = time.time()
        chunks = rag_orchestrator._multi_query_retrieve(
            subq, base_emb, domains, "any", None, sc, primary_query=question)
        dt = round(time.time() - t, 3)

        # (b) Seeded path == streaming pipeline: a provisional rerank of the raw
        #     question (overlapped with the analysis LLM in prod) is reused as seed,
        #     so multi-query only reranks the top-up candidates.
        q_emb = embedding_service.embed_query(question)
        seed = hybrid_retriever.search(question, q_emb, n_results=15, predicted_domains={})
        t = time.time()
        chunks_s = rag_orchestrator._multi_query_retrieve(
            subq, base_emb, domains, "any", None, sc,
            seed_chunks=seed, primary_query=question)
        dt_s = round(time.time() - t, 3)

        row = {"id": cid, "sub_queries": len(subq), "explicit_sc": sc,
               "latency_s": dt, "seeded_latency_s": dt_s,
               "returned": len(chunks), "sc_in_result": sc_count(chunks),
               "seeded_returned": len(chunks_s), "seeded_sc": sc_count(chunks_s)}
        results.append(row)
        print(f"{cid:22s} subq={len(subq)} sc={sc!s:5s} -> sync {dt:5.2f}s (sc={row['sc_in_result']:2d})  "
              f"| stream {dt_s:5.2f}s (sc={row['seeded_sc']:2d})", flush=True)

    avg = sum(r["latency_s"] for r in results) / len(results)
    avg_s = sum(r["seeded_latency_s"] for r in results) / len(results)
    print(f"\nAVG sync retrieval:   {avg:.2f}s", flush=True)
    print(f"AVG stream retrieval: {avg_s:.2f}s (seeded, only tops up the rerank set)", flush=True)
    out = os.path.join("scripts", "multiquery_metrics.json")
    with open(out, "w") as f:
        json.dump({"avg_latency_s": round(avg, 3), "avg_seeded_latency_s": round(avg_s, 3), "rows": results}, f, indent=2)
    print(f"wrote {out}", flush=True)

if __name__ == "__main__":
    main()
