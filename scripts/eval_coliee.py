"""Evaluate BM25 n-gram configurations on the COLIEE-21 task-1 corpus.

Protocol follows U-CREAT (Joshi et al., ACL 2023) Appendix A:
micro-averaged precision, recall and F1 over all queries at top-K,
reported at the K where F1 peaks. Queries are members of the
candidate pool and are excluded from their own rankings.

Labels available locally cover the 650 training queries;
the official COLIEE-21 test set has no public labels.
"""

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import bm25s  # noqa: E402
from legal_rag.retrievers.bm25 import BM25Retriever  # noqa: E402


@dataclass
class Doc:
    id: str
    text: str


class UptoNgramBM25(BM25Retriever):
    """BM25 over the union of word 1..n-grams (ngram_range=(1,n))."""

    def _cache_path(self):
        p = super()._cache_path()
        return p.parent / ("upto_" + p.name)

    def _tokenize(self, texts):
        words = bm25s.tokenize(
            texts, stopwords=[], return_ids=False, show_progress=False
        )
        n = self.ngram
        docs = [
            " ".join(
                "_".join(w[i : i + g]) for g in range(1, n + 1)
                for i in range(len(w) - g + 1)
            )
            for w in words
        ]
        return bm25s.tokenize(docs, stopwords=[], show_progress=False)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True, type=Path)
    ap.add_argument("--ngrams", default="1,2,3,4,5")
    ap.add_argument("--k-max", type=int, default=15)
    ap.add_argument("--cache-dir", type=Path, default=None)
    ap.add_argument("--upto", action="store_true",
                    help="use ngram_range=(1,n) instead of exact n-grams")
    ap.add_argument("--dev", action="store_true",
                    help="evaluate only the repository's dev split")
    args = ap.parse_args()

    doc_dir = args.data_dir / "no_fr"
    docs: dict[str, Doc] = {}
    for p in sorted(doc_dir.glob("*.json")):
        d = json.loads(p.read_text())
        docs[d["id_"]] = Doc(id=d["id_"], text=" ".join(d["body_str"]))
    print(f"{len(docs):,} candidate documents")

    labels = json.loads((args.data_dir / "train_labels.json").read_text())
    labels = {k.replace(".txt", ""): [r.replace(".txt", "") for r in v]
              for k, v in labels.items()}
    if args.dev:
        keep = {k.replace(".txt", "") for k in
                json.loads((args.data_dir / "dev_split.json").read_text())}
        labels = {k: v for k, v in labels.items() if k in keep}
    print(f"{len(labels):,} queries")

    cls = UptoNgramBM25 if args.upto else BM25Retriever
    items = [docs[did] for did in sorted(docs)]
    for ng in [int(x) for x in args.ngrams.split(",")]:
        ret = cls(ngram=ng, cache_dir=args.cache_dir)
        ret.index(items)
        ranks: dict[str, list[str]] = {}
        for qid in labels:
            hits = ret.search(docs[qid].text, top_k=args.k_max + 1)
            ranks[qid] = [h for h, _ in hits if h != qid][: args.k_max]
        rel_total = sum(len(v) for v in labels.values())
        print(f"\nngram={ng}  (micro-F1 by K)")
        best = (0.0, 0)
        for k in range(1, args.k_max + 1):
            tp = sum(len(set(r[:k]) & set(labels[q])) for q, r in ranks.items())
            prec = tp / (len(labels) * k)
            rec = tp / rel_total
            f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
            if f1 > best[0]:
                best = (f1, k)
            print(f"  K={k:2d}  P={prec*100:5.2f}  R={rec*100:5.2f}  F1={f1*100:5.2f}")
        print(f"  best: F1={best[0]*100:.2f} at K={best[1]}")


if __name__ == "__main__":
    main()
