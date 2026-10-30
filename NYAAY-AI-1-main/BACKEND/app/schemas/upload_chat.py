from pydantic import BaseModel, Field

class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    pages: int
    summary: str

from typing import Optional

class ChatQueryRequest(BaseModel):
    document_id: str
    question: str = Field(..., min_length=5, max_length=10000)
    conversation_id: Optional[str] = Field(None, description="Optional ID of an existing conversation to continue")
    language: Optional[str] = "en"
    detected_lang: Optional[str] = "en"

class ChatQueryResponse(BaseModel):
    conversation_id: str
    answer: str
    summary: str
    citations: list[dict] = Field(default_factory=list)
    confidence: dict = Field(..., description="Confidence dictionary")
    advanced_metadata: dict = Field(default_factory=dict)
    metrics: dict = Field(default_factory=dict)
