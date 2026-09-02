from abc import ABC, abstractmethod
from typing import Any

from ..schemas import LegalChunk, LegalDocument


class Retriever(ABC):
    def __init__(self):
        self.items: list[Any] = []

    @abstractmethod
    def index(self, items: list[Any]) -> None:
        ...

    @abstractmethod
    def search(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        ...

    @staticmethod
    def _text(item: Any) -> str:
        return getattr(item, "text", getattr(item, "raw_text", ""))

    @staticmethod
    def _external_id(item: Any) -> str:
        if isinstance(item, LegalChunk):
            return item.parent_doc_id
        if isinstance(item, LegalDocument):
            return item.doc_id
        return getattr(item, "id", str(item))
