"""Fuse the BM25 unigram+context leg with a dense top-100 ranking on
BSARD via reciprocal rank fusion (k=60), and report micro P/R/F1,
MAP, and MRR.

The dense ranking is the output of the remote embedding job
(kaggle/bsard-dense or modal/modal_bsard.py), a JSON object mapping
question id to a ranked list of article ids. The BM25 leg is
rebuilt locally with the same unigram + act-description context
indexing as eval_bsard.py --context.

Usage:
    python scripts/eval_bsard_rrf.py --dense-rankings bsard_dense_top100.json \
        --model-name "Qwen3-0.6B" --out results/bsard/bsard_rrf.json
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from eval_bsard import Doc, load_corpus, load_queries  # noqa: E402
from legal_rag.retrievers.bm25 import BM25Retriever  # noqa: E402

KS = (1, 2, 3, 5, 10, 20, 50, 100)
RRF_K = 60


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dense-rankings", type=Path, required=True,
                    help="JSON {qid: [doc_id, ...]} from the dense job")
    ap.add_argument("--model-name", required=True)
    ap.add_argument("--top", type=int, default=100)
    ap.add_argument("--cache-dir", type=Path, default=Path("data/cache"))
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    dense = json.loads(args.dense_rankings.read_text())
    docs = load_corpus(with_context=True)
    labels, queries = load_queries()
    labels = {q: ids & set(docs) for q, ids in labels.items()}
    rel_total = sum(len(v) for v in labels.values())

    items = [docs[d] for d in sorted(docs)]
    ret = BM25Retriever(ngram=1, cache_dir=args.cache_dir)
    ret.index(items)
    bm25 = {qid: [h for h, _ in ret.search(queries[qid], top_k=args.top)]
            for qid in labels}
    print(f"{len(labels):,} queries fused (BM25 unigram+ctx + "
          f"{args.model_name}, RRF k={RRF_K})")

    fused = {}
    for qid in labels:
        scores = {}
        for rank, did in enumerate(bm25[qid], 1):
            scores[did] = scores.get(did, 0.0) + 1.0 / (RRF_K + rank)
        for rank, did in enumerate(dense.get(qid, []), 1):
            scores[did] = scores.get(did, 0.0) + 1.0 / (RRF_K + rank)
        fused[qid] = sorted(scores, key=scores.get, reverse=True)

    by_k = []
    for k in KS:
        tp = sum(len(set(f[:k]) & ids)
                 for f, ids in zip(fused.values(), labels.values()))
        prec = tp / (len(labels) * k)
        rec = tp / rel_total
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        ap_sum = mrr_sum = 0.0
        for qid, ids in labels.items():
            rr = 0.0
            for i, h in enumerate(fused[qid][:k], 1):
                if h in ids:
                    rr = 1.0 / i
                    break
            mrr_sum += rr
            hits_at = [1 if h in ids else 0 for h in fused[qid][:k]]
            if any(hits_at):
                ap_sum += sum(
                    sum(hits_at[: i + 1]) / (i + 1)
                    for i, x in enumerate(hits_at) if x
                ) / len(ids)
        by_k.append({"k": k, "p": round(prec * 100, 2),
                     "r": round(rec * 100, 2), "f1": round(f1 * 100, 2),
                     "map": round(ap_sum / len(labels) * 100, 2),
                     "mrr": round(mrr_sum / len(labels) * 100, 2)})
        print(f"k={k:<3} P={by_k[-1]['p']:<6} R={by_k[-1]['r']:<6} "
              f"F1={by_k[-1]['f1']:<6} MAP={by_k[-1]['map']:<6} "
              f"MRR={by_k[-1]['mrr']}")

    out = {"model": f"RRF BM25-unigram+ctx + {args.model_name} (k={RRF_K})",
           "dataset": "bsard test", "by_k": by_k}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2))
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
