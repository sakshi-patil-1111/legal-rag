import json
from pathlib import Path
from typing import Any

from .schemas import LegalDocument, LegalQuery


def load_fixture(path: Path) -> tuple[list[LegalDocument], list[LegalQuery]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    docs = [LegalDocument.from_dict(d) for d in data.get("documents", [])]
    queries = [LegalQuery.from_dict(q) for q in data.get("queries", [])]
    return docs, queries


def save_results(path: Path, results: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
