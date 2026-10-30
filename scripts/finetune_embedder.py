"""Contrastive fine-tune of an embedding model on IL-PCSR train split, then dev eval.

Runs on Kaggle/Modal GPU. Trains (query, chunk-of-relevant-doc) pairs with
MultipleNegativesRankingLoss, saves the tuned model, then evaluates dense
retrieval on the dev split for both tasks.

Usage:
  python scripts/finetune_embedder.py --model Qwen/Qwen3-Embedding-0.6B \
      --epochs 1 --batch 8 --max-chunks-per-doc 3
"""
import argparse
import json
import sys
import time
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

DATA = project_root / "data/raw/il_pcsr"
OUT = project_root / "results/ft_qwen3"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-Embedding-0.6B")
    ap.add_argument("--epochs", type=int, default=1)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--max-chunks-per-doc", type=int, default=3)
    ap.add_argument("--chunk-size", type=int, default=512)
    ap.add_argument("--overlap", type=int, default=50)
    ap.add_argument("--max-length", type=int, default=2048)
    ap.add_argument("--eval-topk", type=int, default=10)
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()

    from legal_rag.chunking import RecursiveChunker
    from legal_rag.datasets.il_pcsr import load_il_pcsr
    from legal_rag.metrics import evaluate_query

    chunker = RecursiveChunker(size=args.chunk_size, overlap=args.overlap)

    # chunk the union of both candidate pools once
    chunks_by_task: dict[str, list] = {}
    chunk_lookup: dict[str, dict] = {}
    for task in ("statute", "precedent"):
        _, docs = load_il_pcsr(DATA, "train", task)
        chunks = chunker.chunk(docs)
        chunks_by_task[task] = chunks
        for c in chunks:
            chunk_lookup[c.chunk_id] = {
                "doc_id": c.parent_doc_id,
                "task": task,
                "text": c.text,
            }
    print(
        "chunks: statute %d, precedent %d"
        % (len(chunks_by_task["statute"]), len(chunks_by_task["precedent"])),
        flush=True,
    )

    # -------- training pairs: (query, chunk of each relevant doc) --------
    doc_to_chunks: dict[str, list[str]] = {}
    for cid, c in chunk_lookup.items():
        doc_to_chunks.setdefault(c["doc_id"], []).append(cid)

    raw_queries = json.loads((DATA / "queries.json").read_text())
    pairs = []
    for rq in raw_queries["train_queries"]:
        qt = rq["text"]
        qt = " ".join(qt) if isinstance(qt, list) else qt
        for rel in rq.get("relevant_statute_ids", []) + rq.get(
            "relevant_precedent_ids", []
        ):
            for cid in doc_to_chunks.get(rel, [])[: args.max_chunks_per_doc]:
                pairs.append((qt, chunk_lookup[cid]["text"]))
    print(f"train pairs: {len(pairs):,}", flush=True)

    from datasets import Dataset
    from sentence_transformers import (
        SentenceTransformer,
        SentenceTransformerTrainer,
        SentenceTransformerTrainingArguments,
        losses,
    )

    model = SentenceTransformer(
        args.model,
        model_kwargs={"dtype": "float16"},
        tokenizer_kwargs={"padding_side": "left"},
    )
    model.max_seq_length = args.max_length

    train_ds = Dataset.from_dict(
        {"anchor": [a for a, _ in pairs], "positive": [b for _, b in pairs]}
    )
    loss = losses.MultipleNegativesRankingLoss(model)

    targs = SentenceTransformerTrainingArguments(
        output_dir=str(Path(args.out) / "ckpt"),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch,
        learning_rate=args.lr,
        warmup_ratio=0.05,
        fp16=True,
        logging_steps=50,
        save_strategy="no",
        report_to=[],
    )
    trainer = SentenceTransformerTrainer(
        model=model, args=targs, train_dataset=train_ds, loss=loss
    )
    t0 = time.time()
    trainer.train()
    print(f"[train] done in {(time.time() - t0) / 60:.1f} min", flush=True)

    model.save(str(Path(args.out) / "model"))

    # -------- dev evaluation over the real chunked corpus --------
    import numpy as np

    for task in ("statute", "precedent"):
        task_chunks = chunks_by_task[task]
        texts = [c.text for c in task_chunks]
        print(f"[{task}] encoding {len(texts):,} chunks...", flush=True)
        t0 = time.time()
        c_emb = model.encode(
            texts,
            batch_size=16,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=True,
        )
        print(f"[{task}] encoded in {(time.time() - t0) / 60:.1f} min", flush=True)

        dq, _ = load_il_pcsr(DATA, "dev", task)
        q_emb = model.encode(
            [q.text for q in dq],
            batch_size=8,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        sims = q_emb @ c_emb.T

        agg: dict[str, float] = {}
        per_query = []
        n = 0
        for qi, q in enumerate(dq):
            if not q.ground_truth:
                continue
            order = np.argsort(-sims[qi])[: args.eval_topk * 4]
            seen, preds = set(), []
            for ci in order:
                did = task_chunks[ci].parent_doc_id
                if did not in seen:
                    seen.add(did)
                    preds.append(did)
                if len(preds) >= args.eval_topk:
                    break
            m = evaluate_query(
                [(d, 0.0) for d in preds], set(q.ground_truth), (1, 2, 3, 5, 10)
            )
            per_query.append({"qid": q.qid, "preds": preds, "doc_metrics": m})
            for k_, v in m.items():
                agg[k_] = agg.get(k_, 0.0) + v
            n += 1
        metrics = {k_: v / n for k_, v in agg.items()}
        f1s = {k: v for k, v in metrics.items() if k.startswith("f1@")}
        bk = max(f1s, key=f1s.get)
        print(
            f"FT {task}: f1@10 {100 * metrics['f1@10']:.1f} best {bk} "
            f"{100 * f1s[bk]:.1f} map {100 * metrics['map']:.1f} "
            f"mrr {100 * metrics['mrr']:.1f} r@10 {100 * metrics['recall@10']:.1f}",
            flush=True,
        )
        Path(args.out).mkdir(parents=True, exist_ok=True)
        (Path(args.out) / f"ft_{task}_summary.json").write_text(
            json.dumps({"task": task, "metrics": metrics,
                        "model": args.model, "train_pairs": len(pairs),
                        "epochs": args.epochs}, indent=2)
        )
        (Path(args.out) / f"ft_{task}_per_query.json").write_text(
            json.dumps(per_query)
        )


if __name__ == "__main__":
    main()
