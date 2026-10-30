import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base
import enum

class FeatureType(str, enum.Enum):
    know_kanoon = "know_kanoon"
    upload_chat = "upload_chat"
    legal_reasoning = "legal_reasoning"

class MessageRole(str, enum.Enum):
    user = "user"
    assistant = "assistant"

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(128), nullable=False) # Firebase UID
    title = Column(String(100), nullable=False)
    feature_type = Column(Enum(FeatureType), nullable=False)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=True)
    is_pinned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    document = relationship("Document", back_populates="conversations")


class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False)
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False) # Storing JSON for assistant or text for user
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # User Feedback fields
    is_helpful = Column(String(10), nullable=True) # "yes", "no", or None
    feedback_category = Column(String(50), nullable=True)

    conversation = relationship("Conversation", back_populates="messages")
