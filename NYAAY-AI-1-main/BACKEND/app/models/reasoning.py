import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base

class RetrievalTrace(Base):
    """
    Stores retrieval independently from reasoning.
    Allows regenerating opinions without repeating retrieval, and easier debugging.
    """
    __tablename__ = "retrieval_traces"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False, index=True)
    query_text = Column(Text, nullable=False)
    
    # Stores arrays of retrieved chunk dicts for each category
    retrieved_statutes = Column(JSON, nullable=True)
    retrieved_judgments = Column(JSON, nullable=True)
    retrieved_document_chunks = Column(JSON, nullable=True)
    
    # Store metrics like BM25 scores, Vector scores, generation latency
    metrics = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", backref="retrieval_traces")


class AnalysisSnapshot(Base):
    """
    Immutable Analysis Snapshot for Versioning.
    Whenever the user regenerates the complete Legal Opinion due to new facts or evidence,
    a new snapshot is created.
    """
    __tablename__ = "analysis_snapshots"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    
    # Aggregated facts that led to this snapshot
    facts_provided = Column(Text, nullable=True)
    
    # Optional link to the specific retrieval trace used to generate this snapshot
    retrieval_trace_id = Column(String(36), ForeignKey("retrieval_traces.id"), nullable=True)
    
    # The 14-section card JSON output
    generated_json = Column(JSON, nullable=False)
    
    model_used = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", backref="analysis_snapshots")
    retrieval_trace = relationship("RetrievalTrace")
