import sys, os, time, json
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.knowledge.vector_store import vector_store
from app.knowledge.bm25_manager import bm25_manager
from app.knowledge.embeddings import embedding_service
from app.ai.domain_classifier import domain_classifier
import nltk

QUERIES = {
    "HOMEBUYER": "Developer delayed possession by 4 years, refuses to refund money or pay interest. Force majeure clause being misused. Supreme Court precedent.",
    "MUNICIPAL": "Municipal authority failed to collect garbage for weeks, sanitation problems, public health hazard, I want mandamus against municipal corporation.",
    "EMPLOYMENT": "Employee terminated without hearing, no opportunity to defend, natural justice violated, audi alteram partem, disciplinary proceedings.",
    "SC_DIRECT": "natural justice audi alteram partem disciplinary dismissal fair hearing Supreme Court"
}

def trace_query(label, query):
    print(f"\n{'='*60}")
    print(f"QUERY: {label}")
    print(f"{'='*60}")

    # Domain classification
    t0 = time.time()
    dom = domain_classifier.predict_domain(query)
    print(f"Domain: {dom}")

    # Embedding
    t1 = time.time()
    emb = embedding_service.embed_query(query)
    emb_latency = round(time.time()-t1, 2)
    print(f"Embedding dim: {len(emb)} | latency: {emb_latency}s")

    # Dense retrieval (main collection only, no SC)
    t2 = time.time()
    dense_main = vector_store.search(emb, n_results=10, where=None, search_sc=False)
    dense_latency = round(time.time()-t2, 2)
    print(f"\n--- DENSE (main, no SC) top 10 [{dense_latency}s] ---")
    for i, r in enumerate(dense_main):
        m = r["metadata"]
        print(f"  [{i+1}] dist={r['distance']:.4f} | {m.get('act_name') or m.get('source_name','?')} | {m.get('section','')} | domain={m.get('legal_domain','')}")

    # SC only
    t3 = time.time()
    dense_sc = vector_store.search(emb, n_results=10, where=None, search_sc=True)
    sc_latency = round(time.time()-t3, 2)
    sc_only = [r for r in dense_sc if r.get("id","").startswith("SC_") or r["metadata"].get("case_name")]
    print(f"\n--- DENSE (SC hits from unified top-10) [{sc_latency}s] ---")
    if sc_only:
        for i, r in enumerate(sc_only):
            m = r["metadata"]
            print(f"  [{i+1}] dist={r['distance']:.4f} | {m.get('case_name','?')} | {m.get('source_name','')}")
    else:
        print("  NO SC results in unified top-10")

    # BM25
    t4 = time.time()
    bm25, corpus_ids, corpus_docs, corpus_metas = bm25_manager.get_index("global")
    bm25_latency = round(time.time()-t4, 2)
    if bm25:
        tok = nltk.word_tokenize(query.lower())
        scores = bm25.get_scores(tok)
        ranking = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        print(f"\n--- BM25 top 10 [{bm25_latency}s] ---")
        for rank, idx in enumerate(ranking[:10]):
            m = corpus_metas[idx]
            cid = corpus_ids[idx]
            print(f"  [{rank+1}] score={scores[idx]:.3f} | {m.get('act_name') or m.get('source_name','?')} | {m.get('section','')} | SC={cid.startswith('SC_')}")

    # RRF
    predicted_domains = dom.get("domains", {})
    doc_prio = dom.get("document_type_priority", "any")
    
    def multiplier(meta):
        m = 1.0
        if meta.get("legal_domain","") in predicted_domains:
            m += 0.10 * predicted_domains[meta.get("legal_domain","")]
        if doc_prio != "any" and meta.get("document_type","") == doc_prio:
            m += 0.05
        return m

    initial_k = max(12, int(10 * 1.5))
    dense_all = vector_store.search(emb, n_results=initial_k, where=None, search_sc=True)
    rrf_scores = {}
    for rank, res in enumerate(dense_all):
        base = 1.0 / (60 + rank)
        mul = multiplier(res["metadata"])
        rrf_scores[res["id"]] = rrf_scores.get(res["id"], 0) + base * mul

    if bm25:
        sparse_ranking = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        for rank, idx in enumerate(sparse_ranking[:20]):
            cid = corpus_ids[idx]
            base = 1.0 / (60 + rank)
            mul = multiplier(corpus_metas[idx])
            if cid not in rrf_scores:
                rrf_scores[cid] = base * mul
            else:
                rrf_scores[cid] += base * mul

    sorted_rrf = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:10]
    print(f"\n--- RRF top 10 ---")
    for rank, (cid, score) in enumerate(sorted_rrf):
        # Find metadata
        meta = None
        for r in dense_all:
            if r["id"] == cid:
                meta = r["metadata"]; break
        if meta is None:
            try:
                idx = corpus_ids.index(cid)
                meta = corpus_metas[idx]
            except: meta = {}
        is_sc = cid.startswith("SC_")
        src = meta.get("act_name") or meta.get("source_name") or meta.get("case_name","?")
        dom_hit = meta.get("legal_domain","") in predicted_domains
        mul = multiplier(meta)
        print(f"  [{rank+1}] rrf={score:.5f} | mul={mul:.2f} | SC={is_sc} | {src} | domain_hit={dom_hit}")

for label, query in QUERIES.items():
    trace_query(label, query)

print("\nDone.")
