from dataclasses import dataclass, field, asdict
from typing import Any, Optional


@dataclass
class LegalQuery:
    qid: str
    text: str
    task_type: str
    benchmark: Optional[str] = None
    language: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    ground_truth: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LegalQuery":
        return cls(**data)


@dataclass
class LegalDocument:
    doc_id: str
    doc_type: str
    title: str
    raw_text: str
    source: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LegalDocument":
        return cls(**data)


@dataclass
class LegalChunk:
    chunk_id: str
    parent_doc_id: str
    text: str
    position: int = 0
    chunking_metadata: dict[str, Any] = field(default_factory=dict)
    structural_metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LegalChunk":
        return cls(**data)
