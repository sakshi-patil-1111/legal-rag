from abc import ABC, abstractmethod
from typing import Any

from ..schemas import LegalChunk, LegalDocument


class Retriever(ABC):
    def __init__(self):
        self.items: list[Any] = []
        self._chunk_ids: list[str] = []

    @abstractmethod
    def index(self, items: list[Any]) -> None:
        ...

    @abstractmethod
    def search(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        """Document-level search: returns (parent_doc_id, score), deduplicated."""

    def search_chunks(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        """Chunk-level search: returns (chunk_id, score), NOT deduplicated.

        Default implementation falls back to document-level search.
        Subclasses should override for true chunk-level retrieval.
        """
        return self.search(query, top_k=top_k)

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

    @staticmethod
    def _chunk_id(item: Any) -> str:
        if isinstance(item, LegalChunk):
            return item.chunk_id
        if isinstance(item, LegalDocument):
            return item.doc_id
        return getattr(item, "id", str(item))
