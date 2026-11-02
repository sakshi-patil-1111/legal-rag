"""Evaluate BM25 n-gram configurations on BSARD (Belgian statutory
article retrieval, Louis & Spanakis, ACL 2022).

Public dataset (maastrichtlawtech/bsard): 22,633 French statutory
articles, 222 jurist-labelled test questions. Queries are natural
questions, not corpus members, so no self-exclusion is required.

Protocol matches the repository harness: micro-averaged P/R/F1
reported at the K where F1 peaks, plus MAP@10 and MRR@10.
"""

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from datasets import load_dataset  # noqa: E402
from legal_rag.retrievers.bm25 import BM25Retriever  # noqa: E402


@dataclass
class Doc:
    id: str
    text: str


def load_corpus(with_context: bool) -> dict[str, Doc]:
    rows = load_dataset("maastrichtlawtech/bsard", "corpus", split="corpus")
    docs = {}
    for r in rows:
        text = r["article"] or ""
        if with_context and r.get("description"):
            text = f"{r['description']}\n{text}"
        docs[str(r["id"])] = Doc(id=str(r["id"]), text=text)
    return docs


def load_queries() -> dict[str, set[str]]:
    rows = load_dataset("maastrichtlawtech/bsard", "questions", split="test")
    out = {}
    for r in rows:
        ids = {s.strip() for s in str(r["article_ids"]).split(",") if s.strip()}
        out[str(r["id"])] = ids
    return out, {str(r["id"]): r["question"] for r in rows}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ngrams", default="1,2,3,5")
    ap.add_argument("--k-max", type=int, default=10)
    ap.add_argument("--cache-dir", type=Path, default=Path("data/cache"))
    ap.add_argument("--out-dir", type=Path, default=Path("results/bsard"))
    ap.add_argument("--context", action="store_true",
                    help="prepend act-description path to indexed article text")
    args = ap.parse_args()

    tag = "ctx" if args.context else "art"
    docs = load_corpus(args.context)
    labels, queries = load_queries()
    labels = {q: ids & set(docs) for q, ids in labels.items()}
    print(f"{len(docs):,} articles, {len(labels):,} test questions "
          f"({'with context' if args.context else 'article only'})")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    items = [docs[did] for did in sorted(docs)]
    rel_total = sum(len(v) for v in labels.values())
    summary = {}
    for ng in [int(x) for x in args.ngrams.split(",")]:
        ret = BM25Retriever(ngram=ng, cache_dir=args.cache_dir)
        ret.index(items)
        ranks = {}
        for qid, ids in labels.items():
            hits = ret.search(queries[qid], top_k=args.k_max)
            ranks[qid] = [h for h, _ in hits]

        prec_rec = []
        best = (0.0, 0)
        ap_sum = mrr_sum = 0.0
        for k in range(1, args.k_max + 1):
            tp = sum(len(set(r[:k]) & ids)
                     for r, ids in zip(ranks.values(), labels.values()))
            prec = tp / (len(labels) * k)
            rec = tp / rel_total
            f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
            if f1 > best[0]:
                best = (f1, k)
            prec_rec.append((k, prec, rec, f1))
        for qid, ids in labels.items():
            rr = 0.0
            for i, h in enumerate(ranks[qid][: args.k_max], 1):
                if h in ids:
                    rr = 1.0 / i
                    break
            mrr_sum += rr
            hits_at = [1 if h in ids else 0 for h in ranks[qid][: args.k_max]]
            if any(hits_at):
                ap_sum += sum(
                    sum(hits_at[: i + 1]) / (i + 1)
                    for i, x in enumerate(hits_at) if x
                ) / len(ids)
        f1_map = {
            "ngram": ng,
            "best_f1": round(best[0] * 100, 2),
            "best_k": best[1],
            "map": round(ap_sum / len(labels) * 100, 2),
            "mrr": round(mrr_sum / len(labels) * 100, 2),
            "by_k": [
                {"k": k, "p": round(p * 100, 2), "r": round(r * 100, 2),
                 "f1": round(f * 100, 2)}
                for k, p, r, f in prec_rec
            ],
        }
        summary[f"n{ng}"] = f1_map
        print(f"\nngram={ng}: best F1={f1_map['best_f1']}@K={best[1]}  "
              f"MAP={f1_map['map']}  MRR={f1_map['mrr']}")

    out = {
        "dataset": "maastrichtlawtech/bsard (questions/test)",
        "n_docs": len(docs),
        "n_queries": len(labels),
        "context": args.context,
        "k_max": args.k_max,
        "metrics": summary,
    }
    p = args.out_dir / f"bsard_{tag}.json"
    p.write_text(json.dumps(out, indent=2))
    print(f"\nwrote {p}")


if __name__ == "__main__":
    main()
