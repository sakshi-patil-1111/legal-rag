import os, sys, time
_HERE = os.path.dirname(os.path.abspath(__file__)); _BACKEND = os.path.dirname(_HERE)
os.chdir(_BACKEND); sys.path.insert(0, _BACKEND)

def timeit(fn, *a, **k):
    t = time.time(); r = fn(*a, **k); return round(time.time()-t, 3), r

print("Loading models...", flush=True)
from app.knowledge.embeddings import embedding_service
from app.knowledge.vector_store import vector_store
from app.knowledge.bm25_manager import bm25_manager
from app.knowledge.reranker import reranker_service

Q = "Section 187 BNSS default bail 60 days 90 days life imprisonment police custody"
emb = embedding_service.embed_query(Q)
# warm
_ = vector_store.search(emb, n_results=20, search_sc=True)
bm25, cids, cdocs, cmetas, id2i = bm25_manager.get_index("global")
_ = bm25.get_scores(bm25_manager.tokenize_text(Q))
cand = vector_store.search(emb, n_results=30, search_sc=True)
_ = reranker_service.rerank(Q, [dict(c) for c in cand[:10]], top_k=10)
print("warmed.\n", flush=True)

# dense (2 collections)
dt, dense = timeit(vector_store.search, emb, n_results=20, search_sc=True)
print(f"dense vector_store.search (k=20, 2 collections): {dt}s -> {len(dense)} hits", flush=True)

# bm25
bt, scores = timeit(bm25.get_scores, bm25_manager.tokenize_text(Q))
print(f"bm25 get_scores over corpus ({len(cdocs)} docs)   : {bt}s", flush=True)

# rerank cost at different candidate pool sizes
pool = vector_store.search(emb, n_results=40, search_sc=True)
for N in [40, 30, 20, 15, 10]:
    subset = [dict(c, metadata=dict(c["metadata"])) for c in pool[:N]]
    rt, _ = timeit(reranker_service.rerank, Q, subset, 10)
    print(f"rerank {N:2d} candidates (cross-encoder CPU)      : {rt}s   ({round(rt/N*1000)} ms/pair)", flush=True)
