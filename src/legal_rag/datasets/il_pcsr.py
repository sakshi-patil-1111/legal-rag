import json
from pathlib import Path
from typing import Literal

from ..schemas import LegalDocument, LegalQuery


def _join_text(value: str | list[str]) -> str:
    if isinstance(value, list):
        return " ".join(value)
    return value


def load_il_pcsr(
    data_root: Path,
    split: Literal["train", "dev", "test"],
    task: Literal["statute", "precedent"],
) -> tuple[list[LegalQuery], list[LegalDocument]]:
    queries_path = data_root / "queries.json"
    docs_path = data_root / ("statutes.json" if task == "statute" else "precedents.json")

    raw_queries = json.loads(queries_path.read_text(encoding="utf-8"))
    raw_docs = json.loads(docs_path.read_text(encoding="utf-8"))

    split_key = f"{split}_queries"
    query_list: list[LegalQuery] = []
    for rq in raw_queries.get(split_key, []):
        text = _join_text(rq.get("text", ""))
        gt = rq.get(f"relevant_{task}_ids", [])
        query_list.append(
            LegalQuery(
                qid=rq.get("id", ""),
                text=text,
                task_type=f"{task}_retrieval",
                benchmark="il_pcsr",
                language="en",
                metadata={
                    "case_title": rq.get("case_title", ""),
                    "jurisdiction": rq.get("jurisdiction", ""),
                },
                ground_truth=gt,
            )
        )

    docs: list[LegalDocument] = []
    for rd in raw_docs:
        text = _join_text(rd.get("text", ""))
        title = rd.get("provision_name" if task == "statute" else "case_title", "")
        docs.append(
            LegalDocument(
                doc_id=rd.get("id", ""),
                doc_type="statute" if task == "statute" else "precedent",
                title=title,
                raw_text=text,
                source="il_pcsr",
                metadata=dict(rd),
            )
        )

    return query_list, docs
