import json
from dataclasses import dataclass
from pathlib import Path

from ..schemas import LegalDocument, LegalQuery


@dataclass
class Snippet:
    """A ground-truth snippet from LegalBench-RAG.

    file_path: relative path within corpus/
    span: (char_start, char_end) within the file
    answer: the gold answer text for that span
    """
    file_path: str
    span: tuple[int, int]
    answer: str

    def to_dict(self) -> dict:
        return {"file_path": self.file_path, "span": list(self.span), "answer": self.answer}


def load_legalbench_rag(
    data_root: Path,
    split: str = "test",
    benchmark: str | None = None,
) -> tuple[list[LegalQuery], list[LegalDocument]]:
    """Load LegalBench-RAG data.

    Real data structure (from Dropbox):
      data_root/
        corpus/          # .txt files in subdirs (maud/, cuad/, ...)
        benchmarks/      # {name}.json files with {"tests": [...]}

    Each test case: {"query": str, "snippets": [{"file_path", "span", "answer"}]}

    Fixture data structure (for tests):
      data_root/
        corpus/          # .txt files
        benchmarks/      # test.json with {"test_cases": [{"id", "query", "ground_truth"}]}

    Both formats are handled.

    Ground truth is preserved at two levels:
    - Document-level: query.ground_truth = sorted set of file_paths
    - Snippet-level: query.metadata["snippets"] = list of Snippet dicts
      with file_path, span (char_start, char_end), and answer text.
    """
    corpus_root = data_root / "corpus"
    benchmarks_root = data_root / "benchmarks"

    # --- Load queries from benchmark JSON files ---
    queries: list[LegalQuery] = []

    if benchmark:
        benchmark_files = [benchmarks_root / f"{benchmark}.json"]
    else:
        benchmark_files = sorted(benchmarks_root.glob("*.json"))

    qid_counter = 0
    for bfile in benchmark_files:
        if not bfile.exists():
            continue
        raw = json.loads(bfile.read_text(encoding="utf-8"))

        # Real format: {"tests": [{"query", "snippets": [...]}]}
        # Fixture format: {"test_cases": [{"id", "query", "ground_truth": [...]}]}
        tests = raw.get("tests", raw.get("test_cases", []))
        bench_name = bfile.stem

        for case in tests:
            qid = case.get("id", f"lbr_{bench_name}_{qid_counter}")
            qid_counter += 1

            # Parse snippets (real format) or synthesize from ground_truth (fixture)
            raw_snippets = case.get("snippets", [])
            snippets: list[Snippet] = []
            for s in raw_snippets:
                fp = s.get("file_path", "")
                span = tuple(s.get("span", [0, 0]))
                answer = s.get("answer", "")
                snippets.append(Snippet(file_path=fp, span=span, answer=answer))

            # Document-level ground truth: unique file_paths from snippets
            if snippets:
                gt_files = sorted({s.file_path for s in snippets})
            else:
                gt_files = case.get("ground_truth", [])

            queries.append(
                LegalQuery(
                    qid=str(qid),
                    text=case.get("query", ""),
                    task_type="legal_contract_retrieval",
                    benchmark="legalbench_rag",
                    language="en",
                    ground_truth=gt_files,
                    metadata={
                        "benchmark_subset": bench_name,
                        "snippets": [s.to_dict() for s in snippets],
                    },
                )
            )

    # --- Load corpus documents ---
    docs: list[LegalDocument] = []
    for txt_file in sorted(corpus_root.glob("**/*.txt")):
        rel = txt_file.relative_to(corpus_root).as_posix()
        docs.append(
            LegalDocument(
                doc_id=rel,
                doc_type="contract",
                title=txt_file.stem,
                raw_text=txt_file.read_text(encoding="utf-8"),
                source="legalbench_rag",
                metadata={"file": rel},
            )
        )

    return queries, docs
