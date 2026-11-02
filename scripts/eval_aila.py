"""Evaluate BM25 n-gram configurations on AILA-2019 (FIRE track:
Artificial Intelligence for Legal Assistance, Bhattacharya et
al., FIRE 2019).

Public dataset (Zenodo 4063986): 50 situation-description queries
(~517 words each, Indian Supreme Court), 2,914 prior-case
documents (Task 1, precedent retrieval) and 197 statute
provisions (Task 2, statute retrieval). Relevance judgments are
full graded matrices; labels are pairs with rel >= 1.

Protocol matches the repository harness: micro-averaged P/R/F1
at each cutoff, plus MAP and MRR.

    python scripts/eval_aila.py
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from legal_rag.retrievers.bm25 import BM25Retriever  # noqa: E402

KS = (1, 2, 3, 5, 10, 20, 50, 100)


@dataclass
class Doc:
    id: str
    text: str


def load_queries(path: Path) -> dict[str, str]:
    out = {}
    for line in path.read_text().splitlines():
        if "||" in line:
            qid, text = line.split("||", 1)
            out[qid.strip()] = text.strip()
    return out


def load_qrels(path: Path) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for line in path.read_text().splitlines():
        parts = line.split()
        if len(parts) >= 4 and int(parts[3]) >= 1:
            out.setdefault(parts[0], set()).add(parts[2])
    return out


def load_docs(d: Path, statutes: bool) -> dict[str, Doc]:
    docs = {}
    for f in d.iterdir():
        if statutes:
            raw = f.read_text(errors="replace").splitlines()
            text = " ".join(
                re.sub(r"^(Title|Desc):\s*", "", l) for l in raw
            ).strip()
        else:
            text = f.read_text(errors="replace")
        docs[f.stem] = Doc(id=f.stem, text=text)
    return docs


def evaluate(ranks: dict[str, list[str]], labels: dict[str, set[str]],
             rel_total: int) -> list[dict]:
    by_k = []
    for k in KS:
        tp = sum(len(set(r[:k]) & ids)
                 for r, ids in zip(ranks.values(), labels.values()))
        prec = tp / (len(labels) * k)
        rec = tp / rel_total
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        ap_sum = mrr_sum = 0.0
        for qid, ids in labels.items():
            rr = 0.0
            for i, h in enumerate(ranks[qid][:k], 1):
                if h in ids:
                    rr = 1.0 / i
                    break
            mrr_sum += rr
            hits = [1 if h in ids else 0 for h in ranks[qid][:k]]
            if any(hits):
                ap_sum += sum(
                    sum(hits[: i + 1]) / (i + 1)
                    for i, x in enumerate(hits) if x
                ) / len(ids)
        by_k.append({"k": k, "p": round(prec * 100, 2),
                     "r": round(rec * 100, 2), "f1": round(f1 * 100, 2),
                     "map": round(ap_sum / len(labels) * 100, 2),
                     "mrr": round(mrr_sum / len(labels) * 100, 2)})
    return by_k


def run_task(name: str, docs: dict[str, Doc], queries: dict[str, str],
             labels: dict[str, set[str]], args) -> dict:
    labels = {q: ids & set(docs) for q, ids in labels.items() if q in queries}
    items = [docs[d] for d in sorted(docs)]
    rel_total = sum(len(v) for v in labels.values())
    print(f"\n== {name}: {len(docs):,} docs, {len(labels)} queries, "
          f"{rel_total} relevant")
    summary = {}
    for ng in args.ngrams:
        ret = BM25Retriever(ngram=ng, cache_dir=args.cache_dir)
        ret.index(items)
        ranks = {qid: [h for h, _ in ret.search(queries[qid],
                                                top_k=max(KS))]
                 for qid in labels}
        by_k = evaluate(ranks, labels, rel_total)
        best = max(by_k, key=lambda r: r["f1"])
        summary[f"n{ng}"] = {"best_f1": best["f1"], "best_k": best["k"],
                             "by_k": by_k}
        last = by_k[-1]
        print(f"  ngram={ng}: best F1={best['f1']}@K={best['k']}  "
              f"R@100={last['r']}  MAP@100={last['map']}  "
              f"MRR@100={last['mrr']}")
        if args.save_ranks:
            (args.out_dir / f"aila_{name}_n{ng}_ranks.json").write_text(
                json.dumps(ranks))
    if args.dense_model and name in args.tasks:
        from legal_rag.retrievers.dense import DenseRetriever
        ret = DenseRetriever(model_name=args.dense_model,
                             cache_dir=args.cache_dir,
                             query_prompt="query")
        ret.index(items)
        ranks = {qid: [h for h, _ in ret.search(queries[qid],
                                                top_k=max(KS))]
                 for qid in labels}
        by_k = evaluate(ranks, labels, rel_total)
        best = max(by_k, key=lambda r: r["f1"])
        summary["dense"] = {"model": args.dense_model,
                            "best_f1": best["f1"], "best_k": best["k"],
                            "by_k": by_k}
        last = by_k[-1]
        print(f"  dense={args.dense_model.split('/')[-1]}: "
              f"best F1={best['f1']}@K={best['k']}  "
              f"R@100={last['r']}  MAP@100={last['map']}  "
              f"MRR@100={last['mrr']}")
    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", type=Path, default=Path("data/raw/aila"))
    ap.add_argument("--ngrams", type=int, nargs="+", default=[1, 2, 3, 5])
    ap.add_argument("--dense-model", type=str, default=None,
                    help="HF embedding model for a dense leg on --tasks")
    ap.add_argument("--tasks", nargs="+", default=["statutes"],
                    choices=["statutes", "precedents"])
    ap.add_argument("--cache-dir", type=Path, default=Path("data/cache"))
    ap.add_argument("--save-ranks", action="store_true",
                    help="dump per-query top-100 rankings for fusion")
    ap.add_argument("--out-dir", type=Path, default=Path("results/aila"))
    args = ap.parse_args()

    queries = load_queries(args.data_dir / "Query_doc.txt")
    out = {"dataset": "AILA-2019 (FIRE 2019)", "n_queries": len(queries)}

    out["precedents"] = run_task(
        "precedents",
        load_docs(args.data_dir / "Object_casedocs", statutes=False),
        queries,
        load_qrels(args.data_dir / "relevance_judgments_priorcases.txt"),
        args)
    out["statutes"] = run_task(
        "statutes",
        load_docs(args.data_dir / "Object_statutes", statutes=True),
        queries,
        load_qrels(args.data_dir / "relevance_judgments_statutes.txt"),
        args)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    p = args.out_dir / "aila_bm25.json"
    p.write_text(json.dumps(out, indent=2))
    print(f"\nwrote {p}")


if __name__ == "__main__":
    main()
