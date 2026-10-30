"""Statistical analysis of retrieval results: bootstrap CIs, F1-vs-k
curves, and query-length bucket analysis. Feeds thesis figures/tables.

Usage:
    python scripts/analyze_results.py            # all per-query results
    python scripts/analyze_results.py --out analysis/

Outputs:
    analysis/analysis_summary.json   - per-method stats + CIs
    analysis/fig_f1k_{task}.pdf      - F1 vs k curves
    analysis/fig_len_{task}.pdf      - F1@10 by query-length bucket
    analysis/fig_vs_paper_{task}.pdf - ours vs published baseline bars
"""

import argparse
import glob
import json
import os
import random
from pathlib import Path

KS = [1, 2, 3, 5, 10]

# friendly names for known result files
LABELS = {
    "stage_a_bm25": "BM25 whole-doc",
    "stage_a_bm25_whole": "BM25 whole-doc",
    "phase1": "BM25 baseline",
    "stage_d_fixed512": "BM25 fixed-512",
    "stage_d_recursive": "BM25 rec-512",
    "stage_b_dense": "BGE dense",
    "stage_b_dense_legal": "Legal-Embed",
    "stage_b_dense_sailer": "SAILER",
    "stage_c_hybrid_rrf": "Hybrid RRF (weak)",
    "stage_e_rerank": "Rerank (weak)",
    "stage_h_baseline": "H-baseline",
    "stage_h_final": "H-final",
    "stage_b2_qwen3": "Qwen3-0.6B",
    "stage_b2": "Qwen3-0.6B",
    "stage_a_ngram2": "BM25 2-gram",
    "stage_a_ngram5": "BM25 5-gram",
}

PAPER = {
    "statute": [
        ("BM25 3-gram (paper)", 17.80, 19.39, 41.74),
        ("BM25 para-2gram (paper)", 18.59, 21.82, 44.32),
        ("SAILER infer (paper)", 7.15, 9.31, 19.40),
        ("Para-GNN FT (paper)", 32.85, 44.03, 62.51),
        ("Ensemble (paper)", 39.44, 52.13, 73.77),
    ],
    "precedent": [
        ("BM25 3-gram (paper)", 32.21, 43.44, 57.52),
        ("BM25 5-gram (paper)", 33.29, 43.98, 58.55),
        ("SAILER infer (paper)", 9.94, 13.90, 20.49),
        ("Para-GNN FT (paper)", 22.60, 29.49, 39.22),
        ("Ensemble (paper)", 38.77, 50.21, 63.81),
    ],
}


def method_label(path: str) -> str:
    stem = Path(path).stem
    for suffix in ("_statute", "_precedent", "_summary"):
        if stem.endswith(suffix):
            stem = stem[: -len(suffix)]
    return LABELS.get(stem, stem)


def bootstrap_ci(values: list[float], n_boot: int = 2000, seed: int = 42):
    rng = random.Random(seed)
    n = len(values)
    boots = sorted(
        sum(rng.choices(values, k=n)) / n for _ in range(n_boot)
    )
    lo = boots[int(0.025 * n_boot)]
    hi = boots[int(0.975 * n_boot)]
    return lo, hi


def load_per_query(path: str) -> list[dict]:
    d = json.load(open(path))
    return d.get("per_query") or []


def per_query_metric(queries: list[dict], metric: str) -> list[float]:
    vals = []
    for q in queries:
        m = q.get("doc_metrics") or {}
        if metric in m:
            vals.append(m[metric])
    return vals


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="analysis")
    ap.add_argument("--n-boot", type=int, default=2000)
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(exist_ok=True)

    files = sorted(
        f for f in glob.glob("results/*/*.json")
        if not f.endswith("_summary.json")
        and "phase1_" not in f  # stale pre-stage duplicates
    )

    summary: dict[str, dict] = {}
    per_task_curves: dict[str, dict[str, list[float]]] = {}
    per_task_len: dict[str, dict[str, tuple[list[float], list[float]]]] = {}

    for path in files:
        task = "statute" if path.endswith("_statute.json") else (
            "precedent" if path.endswith("_precedent.json") else None
        )
        if task is None:
            continue
        queries = load_per_query(path)
        if not queries:
            continue
        label = method_label(path)
        stats: dict[str, dict] = {"n": len(queries)}
        for k in KS:
            vals = per_query_metric(queries, f"f1@{k}")
            if not vals:
                continue
            lo, hi = bootstrap_ci(vals, args.n_boot)
            stats[f"f1@{k}"] = {
                "mean": sum(vals) / len(vals), "ci_lo": lo, "ci_hi": hi,
            }
        for metric in ("map", "mrr"):
            vals = per_query_metric(queries, metric)
            if not vals:
                continue
            lo, hi = bootstrap_ci(vals, args.n_boot)
            stats[metric] = {
                "mean": sum(vals) / len(vals), "ci_lo": lo, "ci_hi": hi,
            }
        summary.setdefault(task, {})[label] = stats
        if all(f"f1@{k}" in stats for k in KS):
            per_task_curves.setdefault(task, {})[label] = [
                stats[f"f1@{k}"]["mean"] for k in KS
            ]
        lens = [len(q.get("text", "")) for q in queries]
        f1s = per_query_metric(queries, "f1@10")
        per_task_len.setdefault(task, {})[label] = (lens, f1s)

    # also fold in summary-only results (kaggle runs: ngram, qwen3)
    for path in sorted(glob.glob("results/*/*_summary.json")):
        d = json.load(open(path))
        entries = d.get("tasks") or [d]
        for t in entries:
            task = t.get("task")
            m = t.get("metrics", {})
            label = method_label(path)
            if not task or not m:
                continue
            entry = summary.setdefault(task, {}).setdefault(label, {"n": t.get("n_queries", d.get("n_queries", 0))})
            for k in KS:
                if f"f1@{k}" in m and f"f1@{k}" not in entry:
                    entry[f"f1@{k}"] = {"mean": m[f"f1@{k}"]}
            for metric in ("map", "mrr"):
                if metric in m and metric not in entry:
                    entry[metric] = {"mean": m[metric]}
            if f"f1@{KS[-1]}" in m:
                curve = [m.get(f"f1@{k}", 0.0) for k in KS]
                per_task_curves.setdefault(task, {}).setdefault(label, curve)

    with open(out_dir / "analysis_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    _emit_tex_f1k(per_task_curves, out_dir)
    _emit_tex_len(per_task_len, out_dir)
    _emit_tex_vs_paper(summary, out_dir)
    try:
        _plot_f1k(per_task_curves, out_dir)
        _plot_len(per_task_len, out_dir)
        _plot_vs_paper(summary, out_dir)
    except ImportError:
        pass

    for task, methods in summary.items():
        print(f"\n=== {task} ===")
        for label, s in sorted(methods.items()):
            f1 = s.get("f1@10", {})
            map_s = s.get("map", {})
            mrr = s.get("mrr", {})
            def fmt(x):
                if "ci_lo" in x:
                    return f"{x['mean']*100:5.2f} [{x['ci_lo']*100:.2f},{x['ci_hi']*100:.2f}]"
                return f"{x.get('mean', 0)*100:5.2f}"
            print(f"{label:26s} f1@10={fmt(f1)} map={fmt(map_s)} mrr={fmt(mrr)}")


def _tex_pgfplots(xlabel: str, ylabel: str, series: list, xticklabels=None) -> str:
    """Emit a standalone pgfplots axis block as .tex."""
    lines = [
        "\\begin{tikzpicture}",
        "\\begin{axis}[width=0.46\\linewidth, height=0.34\\linewidth,",
        f"  xlabel={{{xlabel}}}, ylabel={{{ylabel}}},",
        "  legend style={font=\\scriptsize, at={(1.02,1)}, anchor=north west},",
        "  xtick=data, grid=both, grid style={dashed,gray!30},",
        "  mark size=1.8pt, line width=0.8pt]",
    ]
    for label, xs, ys in series:
        coords = " ".join(f"({x},{y:.2f})" for x, y in zip(xs, ys))
        lines.append(f"\\addplot coordinates {{{coords}}};")
        lines.append(f"\\addlegendentry{{{label}}}")
    lines += ["\\end{axis}", "\\end{tikzpicture}"]
    return "\n".join(lines) + "\n"


def _emit_tex_f1k(curves: dict, out_dir: Path) -> None:
    for task, methods in curves.items():
        series = [
            (label, KS, [v * 100 for v in vals])
            for label, vals in methods.items()
        ]
        tex = _tex_pgfplots("$k$", "macro-F1 (\\%)", series)
        (out_dir / f"fig_f1k_{task}.tex").write_text(tex)


def _emit_tex_len(per_task_len: dict, out_dir: Path) -> None:
    keep = {"BM25 rec-512", "Qwen3-0.6B", "BM25 whole-doc", "BGE dense"}
    edges = [0, 8_000, 16_000, 32_000, 64_000, 200_000]
    labels_txt = ["<8k", "8-16k", "16-32k", "32-64k", ">64k"]
    for task, methods in per_task_len.items():
        series = []
        for label, (lens, f1s) in methods.items():
            if label not in keep or not lens:
                continue
            buckets = [[] for _ in range(len(edges) - 1)]
            for ln, f1 in zip(lens, f1s):
                for i in range(len(edges) - 1):
                    if edges[i] <= ln < edges[i + 1]:
                        buckets[i].append(f1)
                        break
            xs = [i for i, b in enumerate(buckets) if b]
            ys = [sum(buckets[i]) / len(buckets[i]) * 100 for i in xs]
            if xs:
                series.append((label, xs, ys))
        if not series:
            continue
        tex = _tex_pgfplots("query length (chars)", "mean F1@10 (\\%)", series)
        (out_dir / f"fig_len_{task}.tex").write_text(tex)


def _emit_tex_vs_paper(summary: dict, out_dir: Path) -> None:
    ours_pick = {
        "statute": ["Qwen3-0.6B", "BM25 2-gram", "BM25 rec-512"],
        "precedent": ["BM25 5-gram", "BM25 2-gram", "BM25 rec-512", "Qwen3-0.6B"],
    }
    for task, paper_rows in PAPER.items():
        methods = summary.get(task, {})
        ours_series, paper_series = [], []
        ys, names = [], []
        idx = 0
        for label in ours_pick.get(task, []):
            s = methods.get(label)
            if s and "f1@10" in s:
                ours_series.append((idx, s["f1@10"]["mean"] * 100))
                names.append(f"ours: {label}")
                ys.append(idx)
                idx += 1
        for name, f1, _, _ in paper_rows:
            paper_series.append((idx, f1))
            names.append(name)
            ys.append(idx)
            idx += 1
        coords_o = " ".join(f"({v:.2f},{i})" for i, v in ours_series)
        coords_p = " ".join(f"({v:.2f},{i})" for i, v in paper_series)
        ticks = ",".join(str(i) for i in ys)
        ticklabels = "{" + ",".join(names) + "}"
        lines = [
            "\\begin{tikzpicture}",
            "\\begin{axis}[xbar, width=0.46\\linewidth, height=0.42\\linewidth,",
            "  xlabel={F1 (\\%)}, bar width=6pt,",
            "  legend style={font=\\scriptsize},",
            "  nodes near coords, every node near coord/.append style={font=\\tiny},",
            f"  ytick={{{ticks}}}, yticklabels={ticklabels},",
            "  yticklabel style={font=\\scriptsize}, y dir=reverse,",
            "  grid=both, grid style={dashed,gray!30}]",
            f"\\addplot[fill=blue!60] coordinates {{{coords_o}}};",
            "\\addlegendentry{ours}",
            f"\\addplot[fill=gray!50] coordinates {{{coords_p}}};",
            "\\addlegendentry{paper}",
            "\\end{axis}",
            "\\end{tikzpicture}",
        ]
        (out_dir / f"fig_vs_paper_{task}.tex").write_text("\n".join(lines) + "\n")


def _plot_f1k(curves: dict, out_dir: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    for task, methods in curves.items():
        fig, ax = plt.subplots(figsize=(5.5, 3.5))
        for label, vals in methods.items():
            ax.plot(KS, [v * 100 for v in vals], marker="o", markersize=3,
                    label=label)
        ax.set_xlabel("k")
        ax.set_ylabel("macro-F1 (%)")
        ax.set_xticks(KS)
        ax.legend(fontsize=7)
        fig.tight_layout()
        fig.savefig(out_dir / f"fig_f1k_{task}.pdf")
        plt.close(fig)


def _plot_len(per_task_len: dict, out_dir: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    keep = {"BM25 rec-512", "Qwen3-0.6B", "BM25 whole-doc", "BGE dense"}
    for task, methods in per_task_len.items():
        fig, ax = plt.subplots(figsize=(5.5, 3.5))
        for label, (lens, f1s) in methods.items():
            if label not in keep or not lens:
                continue
            edges = [0, 8_000, 16_000, 32_000, 64_000, 200_000]
            buckets = [[] for _ in range(len(edges) - 1)]
            for ln, f1 in zip(lens, f1s):
                for i in range(len(edges) - 1):
                    if edges[i] <= ln < edges[i + 1]:
                        buckets[i].append(f1)
                        break
            xs, ys = [], []
            for i, b in enumerate(buckets):
                if b:
                    xs.append(i)
                    ys.append(sum(b) / len(b) * 100)
            labels = ["<8k", "8-16k", "16-32k", "32-64k", ">64k"]
            ax.plot([labels[i] for i in xs], ys, marker="o", markersize=3,
                    label=label)
        ax.set_xlabel("query length (chars)")
        ax.set_ylabel("mean F1@10 (%)")
        ax.legend(fontsize=7)
        fig.tight_layout()
        fig.savefig(out_dir / f"fig_len_{task}.pdf")
        plt.close(fig)


def _plot_vs_paper(summary: dict, out_dir: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ours_pick = {
        "statute": ["Qwen3-0.6B", "BM25 2-gram", "BM25 rec-512"],
        "precedent": ["BM25 5-gram", "BM25 2-gram", "BM25 rec-512", "Qwen3-0.6B"],
    }
    for task, paper_rows in PAPER.items():
        methods = summary.get(task, {})
        names, f1s, colors = [], [], []
        for label in ours_pick.get(task, []):
            s = methods.get(label)
            if s and "f1@10" in s:
                names.append(f"ours: {label}")
                f1s.append(s["f1@10"]["mean"] * 100)
                colors.append("tab:blue")
        for name, f1, _, _ in paper_rows:
            names.append(name)
            f1s.append(f1)
            colors.append("tab:gray")
        fig, ax = plt.subplots(figsize=(6, 3.5))
        ax.barh(range(len(names)), f1s, color=colors)
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names, fontsize=7)
        ax.invert_yaxis()
        ax.set_xlabel("F1 (%)  [ours: F1@10 dev; paper: best-k test]")
        fig.tight_layout()
        fig.savefig(out_dir / f"fig_vs_paper_{task}.pdf")
        plt.close(fig)


if __name__ == "__main__":
    main()
