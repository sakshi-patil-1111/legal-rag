# Import all models here so SQLAlchemy's Base.metadata.create_all()
# can discover them and create the corresponding database tables.
from app.models.user import User  # noqa: F401
from app.models.document import Document  # noqa: F401
from app.models.chat import Conversation, Message  # noqa: F401

__all__ = ["User", "Document", "Conversation", "Message"]
