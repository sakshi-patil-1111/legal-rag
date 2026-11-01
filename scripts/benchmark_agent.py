"""Benchmark the agentic loop vs single-shot retrieval on IL-PCSR.

Arms:
  single_shot : retriever.search(full case text) — no LLM, free
  agent       : route(LLM) -> retrieve -> reflect -> [retrieve] -> synthesise
                one pass emits BOTH agent_r0.json (evidence after first
                retrieve) and agent_r1.json (final evidence + dossier) —
                halves LLM cost vs two independent runs

Metrics per task: F1@k / MAP / MRR / R@10 on the agent's retrieved union
vs ground truth — same evaluator as every other experiment, so numbers
are directly comparable to the retrieval tables. Agent-specific stats:
llm calls, retrieval calls, latency, route choice, reflection-verdict
rate, citation-validity rate (kept vs dropped citations).

Memory note: BM25 legs default to ngram=2 — the unfiltered 5-gram
precedent index (~16.8M shingles) is Kaggle-only. ngram=2 PCR leg
(F1@10 20.1 / MAP 27.1) and LSR leg (10.6/12.6) are the strong local
baselines, so the agent comparison is honest.

Usage:
  python scripts/benchmark_agent.py --limit 5            # smoke test
  python scripts/benchmark_agent.py --limit 100          # full arm
  python scripts/benchmark_agent.py --arms single_shot   # free baseline
"""

import argparse
import json
import sys
import time
from collections import defaultdict
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
from legal_rag.metrics import evaluate_query
from legal_rag.retrievers import BM25Retriever

K_LIST = [1, 2, 3, 5, 10]


def _macro(records: list[dict]) -> dict:
    agg: dict[str, float] = defaultdict(float)
    n = len(records)
    for r in records:
        for k, v in r["metrics"].items():
            agg[k] += v
    return {k: v / n for k, v in agg.items()}


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark the legal agent loop")
    parser.add_argument("--tasks", type=str, default="statute,precedent")
    parser.add_argument("--split", choices=["dev", "test"], default="dev")
    parser.add_argument("--arms", type=str, default="single_shot,agent_r0,agent_r1")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--ngram", type=int, default=2)
    parser.add_argument("--top-k", type=int, default=8)
    parser.add_argument("--out", type=str, default="results/agent_bench")
    args = parser.parse_args()

    tasks = [t.strip() for t in args.tasks.split(",") if t.strip()]
    arms = [a.strip() for a in args.arms.split(",") if a.strip()]
    data_root = project_root / "data" / "raw" / "il_pcsr"
    cache_dir = project_root / "data" / "cache"
    out_dir = project_root / args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    chunker = RecursiveChunker(size=512, overlap=50)
    retrievers, doc_texts, doc_titles = {}, {}, {}
    qids_by_task: dict[str, list] = {}
    import hashlib
    import pickle
    for task in tasks:
        queries, docs = load_il_pcsr(data_root, args.split, task)
        qids_by_task[task] = queries
        doc_texts[task] = {d.doc_id: d.raw_text for d in docs}
        doc_titles[task] = {d.doc_id: d.title for d in docs}
        r = BM25Retriever(ngram=args.ngram, cache_dir=cache_dir)
        t0 = time.perf_counter()
        # chunk cache: RecursiveChunker over 3K precedents takes ~13min in
        # pure python — hash doc texts, pickle chunks once
        h = hashlib.sha256()
        for d in docs:
            h.update(d.raw_text.encode())
        cp = cache_dir / f"chunks_{task}_{args.split}_{h.hexdigest()[:16]}.pkl"
        if cp.exists():
            chunks = pickle.loads(cp.read_bytes())
        else:
            chunks = chunker.chunk(docs)
            cp.parent.mkdir(parents=True, exist_ok=True)
            cp.write_bytes(pickle.dumps(chunks))
        r.index(chunks)
        print(f"[{task}] indexed {len(docs)} docs in {time.perf_counter()-t0:.1f}s",
              flush=True)
        retrievers[task] = r

    # align query sets across tasks by qid
    all_qids = [q.qid for q in qids_by_task[tasks[0]]]
    gt = {t: {q.qid: q.ground_truth for q in qids_by_task[t]} for t in tasks}
    texts = {q.qid: q.text for q in qids_by_task[tasks[0]]}
    eval_qids = all_qids[: args.limit]
    print(f"evaluating {len(eval_qids)} queries x tasks {tasks}", flush=True)

    arms = ["agent" if a in ("agent_r0", "agent_r1") else a for a in arms]
    arms = list(dict.fromkeys(arms))  # dedupe after aliasing

    llm = LLMProvider() if any(a.startswith("agent") for a in arms) else None
    if llm:
        print(f"llm: {llm.provider}/{llm.model}", flush=True)

    for arm in arms:
        arm_records = []
        arm_stats = defaultdict(float)
        t_arm = time.perf_counter()
        agent = None
        if arm in ("agent", "agent_r0", "agent_r1"):
            # single pass with max_extra_rounds=1: evidence snapshot after the
            # first retrieve = r0 arm; final evidence = r1 arm. Halves LLM cost
            # vs two separate runs.
            agent = LegalAgent(retrievers, doc_texts, llm, doc_titles,
                               max_extra_rounds=1, top_k=args.top_k)
            r0_records = []

        for i, qid in enumerate(eval_qids):
            case_text = texts[qid]
            if arm == "single_shot":
                evidence = {t: retrievers[t].search(case_text, top_k=10)
                            for t in tasks}
                dossier, warnings, trace = {}, [], []
                n_reflect_sufficient = 0
                n_retrieve_calls = len(tasks)
                evidence_r0 = None
            else:
                res = agent.run(case_text)
                evidence = {t: res.evidence.get(t, []) for t in tasks}
                dossier, warnings, trace = res.dossier, res.warnings, res.trace
                n_reflect_sufficient = sum(
                    1 for s in trace
                    if s.step == "reflect" and s.detail.get("sufficient"))
                n_retrieve_calls = sum(1 for s in trace if s.step == "retrieve")
                # evidence after the first retrieve step = the r0 arm. Only
                # differs from final evidence when reflection issued new queries.
                evidence_r0 = {}
                for s in trace:
                    if s.step == "retrieve" and not evidence_r0:
                        # cannot reconstruct scores from trace counts alone;
                        # recompute cheaply from the recorded queries
                        for t2, q2 in s.detail["queries"].items():
                            evidence_r0[t2] = retrievers[t2].search(
                                q2, top_k=args.top_k)
                        break

            for task in tasks:
                ranking = evidence.get(task, [])
                m = evaluate_query(ranking, gt[task][qid], K_LIST)
                arm_records.append({"qid": qid, "task": task, "metrics": m,
                                    "n_retrieved": len(ranking)})
                if arm != "single_shot" and evidence_r0:
                    m0 = evaluate_query(evidence_r0.get(task, []),
                                        gt[task][qid], K_LIST)
                    r0_records.append({"qid": qid, "task": task,
                                       "metrics": m0,
                                       "n_retrieved": len(evidence_r0.get(task, []))})

            if arm != "single_shot":
                arm_stats["llm_latency_s"] += sum(
                    s.latency_seconds for s in trace if s.step != "retrieve")
                arm_stats["retrieve_calls"] += n_retrieve_calls
                arm_stats["reflect_sufficient"] += n_reflect_sufficient
                cited = [c.get("id") for k in
                         ("applicable_statutes", "supporting_precedents")
                         for c in dossier.get(k, []) if isinstance(c, dict)]
                dropped = sum(w.count(",") + 1 for w in warnings
                              if "dropped unverifiable" in w)
                arm_stats["citations_kept"] += len(cited)
                arm_stats["citations_dropped"] += dropped
                arm_stats["dossiers_complete"] += int(
                    bool(dossier.get("issue")) and bool(dossier.get("analysis")))

            if (i + 1) % 25 == 0:
                print(f"  [{arm}] {i+1}/{len(eval_qids)} "
                      f"({(time.perf_counter()-t_arm)/60:.1f} min)", flush=True)

        summary = {
            "arm": arm, "split": args.split, "limit": len(eval_qids),
            "ngram": args.ngram, "top_k": args.top_k,
            "wall_min": round((time.perf_counter() - t_arm) / 60, 2),
            "stats": dict(arm_stats),
            "tasks": {t: _macro([r for r in arm_records if r["task"] == t])
                      for t in tasks},
        }
        for t, m in summary["tasks"].items():
            print(f"[{arm}:{t}] f1@10 {100*m['f1@10']:.1f} map {100*m['map']:.1f} "
                  f"mrr {100*m['mrr']:.1f} r@10 {100*m.get('recall@10',0):.1f}",
                  flush=True)
        out_name = "agent_r1" if arm == "agent" else arm
        summary["arm"] = out_name
        json.dump({"summary": summary, "records": arm_records},
                  open(out_dir / f"{out_name}.json", "w"), indent=2)
        print(f"saved {out_dir}/{out_name}.json", flush=True)

        if arm != "single_shot" and r0_records:
            r0_summary = {
                "arm": "agent_r0", "split": args.split,
                "limit": len(eval_qids), "ngram": args.ngram,
                "top_k": args.top_k,
                "note": "evidence snapshot after first retrieve of the r1 run",
                "tasks": {t: _macro([r for r in r0_records if r["task"] == t])
                          for t in tasks},
            }
            for t, m in r0_summary["tasks"].items():
                print(f"[agent_r0:{t}] f1@10 {100*m['f1@10']:.1f} "
                      f"map {100*m['map']:.1f} mrr {100*m['mrr']:.1f} "
                      f"r@10 {100*m.get('recall@10',0):.1f}", flush=True)
            json.dump({"summary": r0_summary, "records": r0_records},
                      open(out_dir / "agent_r0.json", "w"), indent=2)
            print(f"saved {out_dir}/agent_r0.json", flush=True)


if __name__ == "__main__":
    main()
