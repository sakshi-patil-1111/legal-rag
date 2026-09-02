from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from .schemas import LegalChunk, LegalDocument
from .tokenization import tokenize


class Chunker(ABC):
    @abstractmethod
    def chunk(self, documents: list[LegalDocument]) -> list[LegalChunk]:
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        ...


class WholeDocumentChunker(Chunker):
    @property
    def name(self) -> str:
        return "whole"

    def chunk(self, documents: list[LegalDocument]) -> list[LegalChunk]:
        return [
            LegalChunk(
                chunk_id=d.doc_id,
                parent_doc_id=d.doc_id,
                text=d.raw_text,
                position=0,
                chunking_metadata={"strategy": "whole"},
                structural_metadata=d.metadata,
            )
            for d in documents
        ]


@dataclass
class FixedTokenChunker(Chunker):
    size: int = 512
    overlap: int = 0

    @property
    def name(self) -> str:
        return f"fixed_token_{self.size}_{self.overlap}"

    def chunk(self, documents: list[LegalDocument]) -> list[LegalChunk]:
        chunks: list[LegalChunk] = []
        for d in documents:
            tokens = tokenize(d.raw_text)
            start = 0
            idx = 0
            while start < len(tokens):
                end = start + self.size
                chunk_tokens = tokens[start:end]
                chunks.append(
                    LegalChunk(
                        chunk_id=f"{d.doc_id}#c{idx}",
                        parent_doc_id=d.doc_id,
                        text=" ".join(chunk_tokens),
                        position=idx,
                        chunking_metadata={
                            "strategy": self.name,
                            "token_start": start,
                            "token_end": min(end, len(tokens)),
                        },
                        structural_metadata=d.metadata,
                    )
                )
                idx += 1
                if end >= len(tokens):
                    break
                start += self.size - self.overlap
        return chunks


@dataclass
class FixedCharChunker(Chunker):
    size: int = 1024
    overlap: int = 0

    @property
    def name(self) -> str:
        return f"fixed_char_{self.size}_{self.overlap}"

    def chunk(self, documents: list[LegalDocument]) -> list[LegalChunk]:
        chunks: list[LegalChunk] = []
        for d in documents:
            text = d.raw_text
            start = 0
            idx = 0
            while start < len(text):
                end = min(start + self.size, len(text))
                chunks.append(
                    LegalChunk(
                        chunk_id=f"{d.doc_id}#c{idx}",
                        parent_doc_id=d.doc_id,
                        text=text[start:end],
                        position=idx,
                        chunking_metadata={
                            "strategy": self.name,
                            "char_start": start,
                            "char_end": end,
                        },
                        structural_metadata=d.metadata,
                    )
                )
                idx += 1
                if end >= len(text):
                    break
                start += self.size - self.overlap
        return chunks


@dataclass
class RecursiveChunker(Chunker):
    size: int = 512
    overlap: int = 0
    separators: tuple[str, ...] = ("\n\n", "\n", ". ", " ")

    @property
    def name(self) -> str:
        return f"recursive_{self.size}_{self.overlap}"

    def _split_recursive(self, text: str, depth: int = 0) -> list[str]:
        if depth >= len(self.separators):
            return [text]
        sep = self.separators[depth]
        parts = text.split(sep)
        chunks: list[str] = []
        buffer = ""
        for part in parts:
            candidate = (buffer + sep + part) if buffer else part
            if len(tokenize(candidate)) <= self.size:
                buffer = candidate
            else:
                if buffer:
                    chunks.extend(self._split_recursive(buffer, depth + 1))
                buffer = part
        if buffer:
            chunks.extend(self._split_recursive(buffer, depth + 1))
        return chunks

    def chunk(self, documents: list[LegalDocument]) -> list[LegalChunk]:
        chunks: list[LegalChunk] = []
        for d in documents:
            raw_chunks = self._split_recursive(d.raw_text)
            for idx, c in enumerate(raw_chunks):
                chunks.append(
                    LegalChunk(
                        chunk_id=f"{d.doc_id}#c{idx}",
                        parent_doc_id=d.doc_id,
                        text=c,
                        position=idx,
                        chunking_metadata={
                            "strategy": self.name,
                            "depth_used": len(self.separators),
                        },
                        structural_metadata=d.metadata,
                    )
                )
        return chunks
