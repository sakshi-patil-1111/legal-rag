"""Agentic RAG demo: case text -> route -> retrieve -> reflect -> dossier.

Usage:
    python scripts/agent_demo.py --case "tenant deposit withheld by landlord"
    python scripts/agent_demo.py --case-file case.txt --tasks statute,precedent
    python scripts/agent_demo.py --query-id <qid> --legs bm25

Options:
    --legs bm25   ngram-BM25 only (default; no model download, laptop-safe)
    --legs hybrid ngram-BM25 + Qwen3 dense (loads ~1.2GB model for query encode)
    --tasks       comma list, default statute
    --split       dev|test, default dev
    --top-k       docs per corpus per round, default 8
    --rounds      extra reflect/retrieve rounds, default 1
    --json        dump raw result JSON instead of pretty output

Env: GEMINI_API_KEY or LLM_API_KEY (+ LLM_PROVIDER, LLM_BASE_URL, LLM_MODEL)
"""

import argparse
import json
import sys
import time
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    from dotenv import load_dotenv
    load_dotenv(project_root / ".env")
except ImportError:
    pass

from legal_rag.chunking import RecursiveChunker
from legal_rag.datasets import load_il_pcsr
from legal_rag.legal_agent import LegalAgent
from legal_rag.llm import LLMProvider
from legal_rag.retrievers import BM25Retriever, DenseRetriever, HybridRetriever


def build_retriever(legs: str, cache_dir: Path):
    bm25 = BM25Retriever(ngram=5, cache_dir=cache_dir)
    if legs == "bm25":
        return bm25
    dense = DenseRetriever(
        model_name="Qwen/Qwen3-Embedding-0.6B",
        backend="sentence_transformers",
        device="auto",
        dtype="float16",
        query_prompt="query",
        max_length=2048,
        batch_size=4,
        cache_dir=cache_dir,
        show_progress=False,
    )
    return HybridRetriever(bm25, dense)


def main() -> None:
    parser = argparse.ArgumentParser(description="Agentic legal RAG demo")
    src = parser.add_mutually_exclusive_group()
    src.add_argument("--case", type=str)
    src.add_argument("--case-file", type=str)
    src.add_argument("--query-id", type=str)
    parser.add_argument("--tasks", type=str, default="statute")
    parser.add_argument("--legs", choices=["bm25", "hybrid"], default="bm25")
    parser.add_argument("--split", choices=["dev", "test"], default="dev")
    parser.add_argument("--top-k", type=int, default=8)
    parser.add_argument("--rounds", type=int, default=1)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    tasks = [t.strip() for t in args.tasks.split(",") if t.strip()]
    data_root = project_root / "data" / "raw" / "il_pcsr"
    cache_dir = project_root / "data" / "cache"

    chunker = RecursiveChunker(size=512, overlap=50)
    retrievers, doc_texts, doc_titles = {}, {}, {}
    for task in tasks:
        queries, docs = load_il_pcsr(data_root, args.split, task)
        doc_texts[task] = {d.doc_id: d.raw_text for d in docs}
        doc_titles[task] = {d.doc_id: d.title for d in docs}

        r = build_retriever(args.legs, cache_dir)
        t0 = time.perf_counter()
        r.index(chunker.chunk(docs))
        print(f"[{task}] indexed {len(docs)} docs in {time.perf_counter()-t0:.1f}s")
        retrievers[task] = r

    if args.query_id:
        match = [q for q in queries if q.qid == args.query_id]
        if not match:
            sys.exit(f"query id {args.query_id} not found in {args.split} split")
        case_text = match[0].text
    elif args.case_file:
        case_text = Path(args.case_file).read_text(encoding="utf-8")
    elif args.case:
        case_text = args.case
    else:
        sys.exit("provide --case, --case-file, or --query-id")

    agent = LegalAgent(
        retrievers=retrievers,
        doc_texts=doc_texts,
        doc_titles=doc_titles,
        llm=LLMProvider(),
        max_extra_rounds=args.rounds,
        top_k=args.top_k,
    )
    result = agent.run(case_text)

    if args.json:
        print(json.dumps({
            "dossier": result.dossier,
            "evidence": {t: e for t, e in result.evidence.items()},
            "warnings": result.warnings,
            "trace": [
                {"step": s.step, "latency": round(s.latency_seconds, 2)}
                for s in result.trace
            ],
        }, indent=2))
        return

    for s in result.trace:
        print(f"-- {s.step} ({s.latency_seconds:.1f}s)")
        if s.step in ("route", "retrieve"):
            print(f"   {s.detail}")

    d = result.dossier
    print("\n=== DOSSIER ===")
    print(f"Issue: {d.get('issue', '')}")
    for key, label in (("applicable_statutes", "Applicable statutes"),
                      ("supporting_precedents", "Supporting precedents")):
        items = d.get(key, [])
        if items:
            print(f"\n{label}:")
            for c in items:
                print(f"  - {c.get('id')}: {c.get('relevance', '')}")
    print(f"\nAnalysis: {d.get('analysis', '')}")
    print(f"\nSuggested action: {d.get('suggested_action', '')}")
    for w in result.warnings:
        print(f"\n[warning] {w}")


if __name__ == "__main__":
    main()
