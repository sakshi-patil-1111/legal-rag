"""BGE-M3 all-modes evaluation on IL-PCSR dev split.

Runs on Kaggle GPU. Encodes the chunked corpus with BGE-M3 once, then evaluates:
  - dense leg (cosine)
  - sparse leg (learned lexical weights)
  - RRF union of dense+sparse
  - ColBERT late-interaction MaxSim rerank over the union pool (top 50+50)

ColBERT vectors are computed only for pooled candidates (full-corpus token-level
storage would not fit memory); candidates are cached across queries.

Usage:
  python scripts/run_bgem3.py --pool 50 --colbert-pool 60
"""
import argparse
import json
import sys
import time
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

DATA = project_root / "data/raw/il_pcsr"
OUT = project_root / "results/bgem3"


def rrf_merge(rank_lists: list[list[str]], k: int = 60) -> list[str]:
    scores: dict[str, float] = {}
    for rl in rank_lists:
        for rank, did in enumerate(rl):
            scores[did] = scores.get(did, 0.0) + 1.0 / (k + rank + 1)
    return sorted(scores, key=scores.get, reverse=True)


def aggregate(rankings, truths, eval_topk):
    from legal_rag.metrics import evaluate_query

    agg: dict[str, float] = {}
    n = 0
    for preds, gt in zip(rankings, truths):
        if not gt:
            continue
        m = evaluate_query(
            [(d, 0.0) for d in preds[:eval_topk]], set(gt), (1, 2, 3, 5, 10)
        )
        for k_, v in m.items():
            agg[k_] = agg.get(k_, 0.0) + v
        n += 1
    return {k_: v / n for k_, v in agg.items()}


def report(tag, metrics):
    f1s = {k: v for k, v in metrics.items() if k.startswith("f1@")}
    bk = max(f1s, key=f1s.get)
    print(
        f"{tag}: f1@10 {100 * metrics['f1@10']:.1f} best {bk} {100 * f1s[bk]:.1f} "
        f"map {100 * metrics['map']:.1f} mrr {100 * metrics['mrr']:.1f} "
        f"r@10 {100 * metrics['recall@10']:.1f}",
        flush=True,
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="BAAI/bge-m3")
    ap.add_argument("--chunk-size", type=int, default=512)
    ap.add_argument("--overlap", type=int, default=50)
    ap.add_argument("--pool", type=int, default=50)
    ap.add_argument("--colbert-pool", type=int, default=60)
    ap.add_argument("--eval-topk", type=int, default=10)
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()

    from legal_rag.chunking import RecursiveChunker
    from legal_rag.datasets.il_pcsr import load_il_pcsr

    chunker = RecursiveChunker(size=args.chunk_size, overlap=args.overlap)

    from FlagEmbedding import BGEM3FlagModel

    model = BGEM3FlagModel(args.model, use_fp16=True)

    for task in ("statute", "precedent"):
        dq, docs = load_il_pcsr(DATA, "dev", task)
        chunks = chunker.chunk(docs)
        texts = [c.text for c in chunks]
        print(f"[{task}] {len(chunks):,} chunks; encoding dense+sparse...", flush=True)
        t0 = time.time()
        out = model.encode(
            texts,
            batch_size=16,
            max_length=1024,
            return_dense=True,
            return_sparse=True,
            return_colbert_vecs=False,
        )
        dense = out["dense_vecs"]
        lex = out["lexical_weights"]  # list of dict token->weight
        print(f"[{task}] encoded in {(time.time() - t0) / 60:.1f} min", flush=True)

        import numpy as np

        # inverted index for sparse leg
        inv: dict[str, list[tuple[int, float]]] = {}
        for ci, w in enumerate(lex):
            for tok, wt in w.items():
                inv.setdefault(tok, []).append((ci, float(wt)))

        # encode queries in small batches; colbert lazily in the rerank phase
        # (a full-corpus batch of 4096-len colbert vecs OOMs host RAM)
        q_dense_l, q_lex_l = [], []
        QB = 16
        for i in range(0, len(dq), QB):
            qb = model.encode(
                [q.text for q in dq[i : i + QB]],
                batch_size=2,
                max_length=4096,
                return_dense=True,
                return_sparse=True,
                return_colbert_vecs=False,
            )
            q_dense_l.append(qb["dense_vecs"])
            q_lex_l.extend(qb["lexical_weights"])
        q_dense = np.concatenate(q_dense_l)
        q_lex = q_lex_l

        # doc-level dedup helper
        def dedup_chunk_ranking(chunk_order, k):
            seen, preds = set(), []
            for ci in chunk_order:
                did = chunks[ci].parent_doc_id
                if did not in seen:
                    seen.add(did)
                    preds.append(did)
                if len(preds) >= k:
                    break
            return preds

        dense_rankings, sparse_rankings, hybrid_rankings = [], [], []
        pools: list[list[int]] = []
        for qi in range(len(dq)):
            d_order = np.argsort(-(q_dense[qi] @ dense.T))[: args.pool]
            s_scores: dict[int, float] = {}
            for tok, wt in q_lex[qi].items():
                for ci, cwt in inv.get(tok, []):
                    s_scores[ci] = s_scores.get(ci, 0.0) + float(wt) * cwt
            s_order = sorted(s_scores, key=s_scores.get, reverse=True)[: args.pool]
            dense_rankings.append(dedup_chunk_ranking(d_order, args.pool))
            sparse_rankings.append(dedup_chunk_ranking(s_order, args.pool))
            pool = list(dict.fromkeys(list(d_order) + list(s_order)))[
                : args.colbert_pool
            ]
            pools.append(pool)
            hybrid_rankings.append(
                rrf_merge(
                    [
                        [chunks[ci].parent_doc_id for ci in d_order],
                        [chunks[ci].parent_doc_id for ci in s_order],
                    ]
                )[: args.eval_topk]
            )

        truths = [q.ground_truth for q in dq]
        for name, ranks in (
            ("dense", dense_rankings),
            ("sparse", sparse_rankings),
            ("hybrid_rrf", hybrid_rankings),
        ):
            m = aggregate(ranks, truths, args.eval_topk)
            report(f"bge-m3 {task} {name}", m)
            Path(args.out).mkdir(parents=True, exist_ok=True)
            (Path(args.out) / f"{task}_{name}_summary.json").write_text(
                json.dumps({"task": task, "method": name, "metrics": m}, indent=2)
            )

        # -------- ColBERT MaxSim rerank over union pools --------
        import torch

        needed = sorted({ci for pool in pools for ci in pool})
        print(
            f"[{task}] encoding colbert for {len(needed):,} pooled chunks...",
            flush=True,
        )
        t0 = time.time()
        col_vecs: dict[int, np.ndarray] = {}
        B = 8
        for i in range(0, len(needed), B):
            batch_ids = needed[i : i + B]
            batch_out = model.encode(
                [texts[ci] for ci in batch_ids],
                batch_size=len(batch_ids),
                max_length=1024,
                return_dense=False,
                return_sparse=False,
                return_colbert_vecs=True,
            )
            for ci, v in zip(batch_ids, batch_out["colbert_vecs"]):
                col_vecs[ci] = v
        print(f"[{task}] colbert encoded in {(time.time() - t0) / 60:.1f} min", flush=True)

        col_rankings = []
        for qi in range(len(dq)):
            qc = model.encode(
                [dq[qi].text],
                batch_size=1,
                max_length=4096,
                return_dense=False,
                return_sparse=False,
                return_colbert_vecs=True,
            )["colbert_vecs"][0]
            qv = torch.tensor(qc, dtype=torch.float32)
            scores = []
            for ci in pools[qi]:
                dv = torch.tensor(col_vecs[ci], dtype=torch.float32)
                sim = qv @ dv.T  # (q_tok, d_tok)
                scores.append((float(sim.max(dim=1).values.sum()), ci))
            order = [ci for _, ci in sorted(scores, reverse=True)]
            col_rankings.append(dedup_chunk_ranking(order, args.eval_topk))
        m = aggregate(col_rankings, truths, args.eval_topk)
        report(f"bge-m3 {task} colbert_rerank", m)
        (Path(args.out) / f"{task}_colbert_rerank_summary.json").write_text(
            json.dumps({"task": task, "method": "colbert_rerank", "metrics": m},
                       indent=2)
        )


if __name__ == "__main__":
    main()
