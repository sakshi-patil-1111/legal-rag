"""CPU-only retrieval experiments: PRF expansion + rhetorical-role queries.

Builds an n-gram BM25 index over the IL-PCSR corpus (with optional min-df
vocab filtering for memory safety on small machines), then evaluates:

  --experiment prf    pseudo-relevance feedback: expand the query with the
                      top shingles harvested from the first-pass top docs
  --experiment roles  restrict the query to selected rhetorical-role segments
  --experiment base   plain baseline on the same filtered index (control)

Usage:
  nice -10 .venv/bin/python scripts/run_cpu_experiments.py \
      --experiment prf --task precedent --ngram 5 --min-df 2 --top-d 5 --expand 15
"""
import argparse
import hashlib
import json
import pickle
import sys
import time
from collections import Counter
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

import bm25s

from legal_rag.metrics import evaluate_query

DATA = project_root / "data/raw/il_pcsr"
CACHE = project_root / "data/cache_cpu"

ROLE_PRESETS = {
    "facts_issue": ["Facts", "Issue"],
    "issue": ["Issue"],
    "facts": ["Facts"],
    "no_reasoning": [
        "Facts", "Issue", "Argument by Petitioner", "Argument by Respondent",
        "Statute Analysis", "Precedent Analysis", "Court Disclosure", "NONE",
    ],
    "analysis": ["Statute Analysis", "Precedent Analysis"],
}


def word_tokens(text: str) -> list[str]:
    return bm25s.tokenize([text], stopwords=[], return_ids=False, show_progress=False)[0]


def shingles(words: list[str], n: int) -> list[str]:
    if n <= 1:
        return list(words)
    return ["_".join(words[i : i + n]) for i in range(len(words) - n + 1)]


def corpus_key(docs: list[str], ngram: int, min_df: int) -> str:
    h = hashlib.sha256(f"n{ngram}-df{min_df}".encode())
    for t in docs[:200]:
        h.update(t[:2000].encode())
    h.update(str(len(docs)).encode())
    return h.hexdigest()[:16]


def build_index(docs: list[str], ngram: int, min_df: int):
    """Tokenize -> optional df filter -> bm25s index. Returns (bm25, doc_shingles)."""
    CACHE.mkdir(parents=True, exist_ok=True)
    key = corpus_key(docs, ngram, min_df)
    cache_dir = CACHE / f"idx_{key}"
    toks_file = CACHE / f"toks_{key}.pkl"
    if cache_dir.exists() and toks_file.exists():
        print(f"[cache] loading index {key}")
        model = bm25s.BM25.load(str(cache_dir), show_progress=False)
        with open(toks_file, "rb") as f:
            doc_toks = pickle.load(f)
        return model, doc_toks

    t0 = time.time()
    doc_toks: list[list[str]] = []
    df: Counter = Counter()
    for i, text in enumerate(docs):
        toks = shingles(word_tokens(text), ngram)
        doc_toks.append(toks)
        df.update(set(toks))
        if (i + 1) % 500 == 0:
            print(f"  tokenized {i + 1}/{len(docs)} ({time.time() - t0:.0f}s)", flush=True)

    vocab = {t for t, c in df.items() if c >= min_df}
    print(f"vocab: {len(df):,} -> {len(vocab):,} shingles (min_df={min_df})")
    if min_df > 1:
        doc_toks = [[t for t in toks if t in vocab] for toks in doc_toks]

    joined = [" ".join(toks) for toks in doc_toks]
    corpus_tokens = bm25s.tokenize(joined, stopwords=[], show_progress=False)
    model = bm25s.BM25(k1=1.6, b=0.7)
    model.index(corpus_tokens, show_progress=False)
    model.save(str(cache_dir), show_progress=False)
    with open(toks_file, "wb") as f:
        pickle.dump(doc_toks, f, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"[index] built in {time.time() - t0:.0f}s -> {cache_dir}")
    return model, doc_toks


def retrieve(model: bm25s.BM25, query_toks: list[str], k: int = 10):
    import bm25s as _b
    res, scores = model.retrieve(
        _b.tokenize([" ".join(query_toks)], stopwords=[], show_progress=False),
        k=k, corpus=None, show_progress=False,
    )
    return [(int(i), float(s)) for i, s in zip(res[0], scores[0])]


def macro_eval(rankings: list[list[str]], truths: list[set], ks=(1, 2, 3, 5, 10)):
    agg: dict[str, float] = {}
    n = 0
    for preds, gt in zip(rankings, truths):
        if not gt:
            continue
        m = evaluate_query([(p, 0.0) for p in preds], gt, ks)
        for k_, v in m.items():
            agg[k_] = agg.get(k_, 0.0) + v
        n += 1
    return {k_: v / max(n, 1) for k_, v in agg.items()}


def show(name: str, metrics: dict):
    f1s = {k: v for k, v in metrics.items() if k.startswith("f1@")}
    bk = max(f1s, key=f1s.get)
    print(
        f"{name:>22} | f1@10 {100 * metrics.get('f1@10', 0):5.1f} | best {bk} "
        f"{100 * f1s[bk]:5.1f} | map {100 * metrics.get('map', 0):5.1f} | "
        f"mrr {100 * metrics.get('mrr', 0):5.1f} | r@10 {100 * metrics.get('recall@10', 0):5.1f}"
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--experiment", choices=["prf", "roles", "base"], required=True)
    ap.add_argument("--task", default="precedent", choices=["precedent", "statute"])
    ap.add_argument("--split", default="dev")
    ap.add_argument("--ngram", type=int, default=5)
    ap.add_argument("--min-df", type=int, default=2)
    ap.add_argument("--top-d", type=int, default=5, help="PRF feedback docs")
    ap.add_argument("--expand", type=int, default=15, help="PRF expansion terms")
    ap.add_argument("--roles", default="facts_issue",
                    help="comma list or preset: " + ",".join(ROLE_PRESETS))
    ap.add_argument("--top-k", type=int, default=10)
    args = ap.parse_args()

    queries_raw = json.loads((DATA / "queries.json").read_text())[
        f"{args.split}_queries"
    ]
    docs_raw = json.loads(
        (DATA / ("precedents.json" if args.task == "precedent" else "statutes.json")).read_text()
    )
    doc_ids = [d["id"] for d in docs_raw]
    doc_texts = ["\n".join(d["text"]) if isinstance(d["text"], list) else d["text"] for d in docs_raw]
    rel_key = f"relevant_{'precedent' if args.task == 'precedent' else 'statute'}_ids"
    truths = [set(q.get(rel_key, [])) for q in queries_raw]

    print(f"task={args.task} queries={len(queries_raw)} docs={len(doc_ids)}")
    model, doc_toks = build_index(doc_texts, args.ngram, args.min_df)
    print(f"[mem] index ready; vocab={len(model.scores.get('vocab', {})) or '?'}")

    def full_query(q: dict) -> str:
        t = q["text"]
        return "\n".join(t) if isinstance(t, list) else t

    def role_query(q: dict, roles: list[str]) -> str:
        segs = q.get("text", [])
        rr = q.get("rhetorical_roles", [])
        if not isinstance(segs, list) or len(segs) != len(rr):
            return full_query(q)
        keep = [s for s, r in zip(segs, rr) if r in roles]
        return "\n".join(keep) if keep else full_query(q)

    top_k = args.top_k
    rankings: list[list[str]] = []

    label = "base"
    if args.experiment == "base":
        for q in queries_raw:
            hits = retrieve(model, shingles(word_tokens(full_query(q)), args.ngram), top_k)
            rankings.append([doc_ids[i] for i, _ in hits])
    elif args.experiment == "roles":
        roles = ROLE_PRESETS.get(args.roles) or args.roles.split(",")
        label = f"roles={args.roles}"
        for q in queries_raw:
            hits = retrieve(model, shingles(word_tokens(role_query(q, roles)), args.ngram), top_k)
            rankings.append([doc_ids[i] for i, _ in hits])
    else:
        label = f"prf d={args.top_d} e={args.expand}"
        for qi, q in enumerate(queries_raw):
            q_toks = shingles(word_tokens(full_query(q)), args.ngram)
            first = retrieve(model, q_toks, args.top_d)
            doc_idx = [i for i, _ in first]
            q_set = set(q_toks)
            pool: Counter = Counter()
            for di in doc_idx:
                pool.update(doc_toks[di])
            expansion = [t for t, _ in pool.most_common(50) if t not in q_set][: args.expand]
            second = retrieve(model, q_toks + expansion, top_k)
            rankings.append([doc_ids[i] for i, _ in second])
            if (qi + 1) % 100 == 0:
                print(f"  prf {qi + 1}/{len(queries_raw)}", flush=True)
    show(label, macro_eval(rankings, truths))

    out = {
        "experiment": args.experiment,
        "args": vars(args),
        "metrics": macro_eval(rankings, truths),
        "per_query": [
            {"id": q["id"], "preds": r, "gt": sorted(g)}
            for q, r, g in zip(queries_raw, rankings, truths)
        ],
    }
    outdir = project_root / "results" / f"cpu_{args.experiment}_{args.task}"
    outdir.mkdir(parents=True, exist_ok=True)
    tag = f"n{args.ngram}_df{args.min_df}"
    if args.experiment == "prf":
        tag += f"_d{args.top_d}e{args.expand}"
    if args.experiment == "roles":
        tag += f"_{args.roles}"
    path = outdir / f"{tag}.json"
    path.write_text(json.dumps(out))
    print(f"saved -> {path}")


if __name__ == "__main__":
    main()
