from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.orm import validates

from app.database.database import Base


class User(Base):
    """
    SQLAlchemy model for the users table.
    Stores user profile data synchronized from Firebase Auth.
    firebase_uid is the canonical user identifier — no passwords stored locally.
    """

    __tablename__ = "users"

    firebase_uid = Column(String, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    name = Column(String, nullable=False)
    role = Column(
        String,
        nullable=False,
        comment="One of: citizen, student, lawyer"
    )
    preferences = Column(Text, nullable=True, default="{}")
    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    last_login = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    @validates("role")
    def validate_role(self, key, value):
        valid_roles = {"citizen", "student", "lawyer"}
        norm_val = str(value).strip().lower() if value else "citizen"
        if norm_val not in valid_roles:
            raise ValueError(
                f"Invalid role '{value}'. Must be one of: {', '.join(sorted(valid_roles))}"
            )
        return norm_val

    def __repr__(self):
        return f"<User firebase_uid={self.firebase_uid!r} email={self.email!r} role={self.role!r}>"
