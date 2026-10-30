import os, sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.knowledge.embeddings import embedding_service
from app.knowledge.hybrid_retriever import hybrid_retriever
from app.knowledge.metadata_utils import get_canonical_source_name

QUERIES = [
    "tenant eviction notice period",
    "police refusing to register FIR",
    "maternity leave entitlement",
    "consumer complaint for defective product",
    "wrongful salary deduction",
    "what are my fundamental rights regarding freedom of speech",
    "property registration process and mutation",
    "divorce by mutual consent cooling off period",
]

def classify(chunk):
    meta = chunk.get("metadata", {})
    cid = chunk.get("id", "") or ""
    src = get_canonical_source_name(meta) or ""
    dt = meta.get("document_type", "")
    court = meta.get("court", "") or meta.get("court_level", "")
    if dt == "statute" or "Act" in src or "Sanhita" in src:
        return "statute", src
    if cid.startswith("SC_") or dt == "judgment" or court == "Supreme Court" or "Supreme Court" in src:
        return "sc", src
    return "other", src

tot_sc = tot_st = tot_ot = 0
print("=== BALANCE CHECK (direct hybrid_retriever.search, top 10) ===")
for q in QUERIES:
    emb = embedding_service.embed_query(q)
    res = hybrid_retriever.search(q, emb, n_results=10)
    sc = st = ot = 0
    srcs = []
    for c in res:
        kind, src = classify(c)
        if kind == "statute": st += 1
        elif kind == "sc": sc += 1
        else: ot += 1
        srcs.append(f"{kind[:2].upper()}:{src[:32]}")
    tot_sc += sc; tot_st += st; tot_ot += ot
    print(f"\nQ: {q}")
    print(f"   returned={len(res)}  SC={sc}  Statute={st}  Other={ot}")
    for s in srcs:
        print(f"     - {s}")

n = len(QUERIES)
print("\n=== AVERAGES over %d queries ===" % n)
print(f"   avg SC per query      : {tot_sc/n:.1f}")
print(f"   avg Statute per query : {tot_st/n:.1f}")
print(f"   avg Other per query   : {tot_ot/n:.1f}")
