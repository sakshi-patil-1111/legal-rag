"""
auth_service.py — Business logic for user management.

All database operations for the auth flow are centralised here.
Routes remain thin and delegate to these functions.
"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.user import User


def get_user_by_uid(db: Session, firebase_uid: str) -> User | None:
    """
    Look up a user by their Firebase UID.
    Returns None if no matching user is found.
    """
    return db.query(User).filter(User.firebase_uid == firebase_uid).first()


def update_last_login(db: Session, firebase_uid: str) -> User | None:
    """
    Update the last_login timestamp for an existing user.
    Returns the updated user, or None if the user does not exist.
    """
    user = get_user_by_uid(db, firebase_uid)
    if user:
        user.last_login = datetime.now(timezone.utc)
        db.commit()
        db.refresh(user)
    return user


def create_user(
    db: Session,
    firebase_uid: str,
    email: str,
    name: str,
    role: str,
) -> User:
    """
    Insert a new user record into the database.
    Raises ValueError if the role is invalid (enforced at ORM level).
    """
    now = datetime.now(timezone.utc)
    user = User(
        firebase_uid=firebase_uid,
        email=email,
        name=name,
        role=role,
        preferences="{}",
        created_at=now,
        last_login=now,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def sync_user(
    db: Session,
    firebase_uid: str,
    email: str,
    name: str,
    role: str,
) -> User:
    """
    Create a new user, or update an existing user's profile.

    Used during:
    - First email/password signup → create
    - First Google login (after role selection) → create
    - Subsequent logins → update last_login only (name/role preserved)

    Returns the created or updated User.
    """
    user = get_user_by_uid(db, firebase_uid)
    if user is None:
        return create_user(db, firebase_uid, email, name, role)

    # User already exists: update mutable fields and last_login
    user.name = name
    user.role = role
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return user
