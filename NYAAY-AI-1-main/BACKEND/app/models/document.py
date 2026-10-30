from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)
    user_uid = Column(String, ForeignKey("users.firebase_uid"), nullable=False, index=True)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    pages = Column(Integer, nullable=False, default=1)
    extracted_text = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    uploaded_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User")
    conversations = relationship("Conversation", back_populates="document")

    def __repr__(self):
        return f"<Document id={self.id!r} filename={self.filename!r} pages={self.pages}>"
