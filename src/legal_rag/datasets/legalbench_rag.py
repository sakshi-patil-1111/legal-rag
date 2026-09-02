import json
from pathlib import Path

from ..schemas import LegalDocument, LegalQuery


def load_legalbench_rag(
    data_root: Path,
    split: str = "test",
) -> tuple[list[LegalQuery], list[LegalDocument]]:
    corpus_root = data_root / "corpus"
    benchmark_path = data_root / "benchmarks" / f"{split}.json"

    raw = json.loads(benchmark_path.read_text(encoding="utf-8"))
    cases = raw.get("test_cases", raw if isinstance(raw, list) else [])

    queries: list[LegalQuery] = []
    for case in cases:
        queries.append(
            LegalQuery(
                qid=case.get("id", ""),
                text=case.get("query", ""),
                task_type="legal_contract_retrieval",
                benchmark="legalbench_rag",
                language="en",
                ground_truth=case.get("ground_truth", []),
            )
        )

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
