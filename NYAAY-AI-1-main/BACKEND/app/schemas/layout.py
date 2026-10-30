from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum

class BlockType(str, Enum):
    TITLE = "title"
    METADATA_TABLE = "metadata_table"
    PARTIES_TABLE = "parties_table"
    SUBJECT = "subject"
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    NUMBERED_PARAGRAPH = "numbered_paragraph"
    SIGNATURE_BLOCK = "signature_block"
    VERIFICATION_BLOCK = "verification_block"
    ANNEXURE_LIST = "annexure_list"
    PAGE_BREAK = "page_break"
    SPACER = "spacer"

class ASTNode(BaseModel):
    id: str
    type: BlockType
    content: Any
    metadata: Dict[str, Any] = Field(default_factory=dict)
    children: List["ASTNode"] = Field(default_factory=list)

class DocumentAST(BaseModel):
    nodes: List[ASTNode] = Field(default_factory=list)
