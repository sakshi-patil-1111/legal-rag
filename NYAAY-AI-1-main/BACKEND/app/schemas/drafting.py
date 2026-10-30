from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class DocumentMetadata(BaseModel):
    version: int = 1
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    language: str = "en"
    
class VerificationSchema(BaseModel):
    date: str = "[Date]"
    place: str = "[Place]"
    text: str = ""

class StructuredDocumentObject(BaseModel):
    document_type: str
    title: str
    metadata: DocumentMetadata = Field(default_factory=DocumentMetadata)
    parties: Dict[str, str] = Field(default_factory=dict)
    body: List[str] = Field(default_factory=list)
    annexures: List[str] = Field(default_factory=list)
    signature_blocks: List[str] = Field(default_factory=list)
    verification: Optional[VerificationSchema] = None
    missing_fields: List[str] = Field(default_factory=list)
    citations_used: List[str] = Field(default_factory=list)
