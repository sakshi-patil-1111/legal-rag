"""
test_milestone1.py - Milestone 1 verification script.

Tests:
  1. User model: valid instantiation
  2. User model: invalid role raises ValueError
  3. auth_service: all functions importable
  4. Middleware: no token -> 401
  5. Middleware: invalid token -> 401
  6. SQLite: users table exists with correct columns and DATETIME types
"""

import sys
import os

# Add BACKEND/ to sys.path so 'app' is importable regardless of working directory
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

results = []


def check(label, ok, detail=""):
    results.append((label, ok, detail))
    tag = "[PASS]" if ok else "[FAIL]"
    suffix = f"  -> {detail}" if detail else ""
    print(f"{tag} {label}{suffix}")


# ── 1. User model: valid instantiation ───────────────────────────────────────
try:
    from app.models.user import User
    from datetime import datetime, timezone

    u = User(
        firebase_uid="uid_test_123",
        email="test@nyaay.ai",
        name="Test User",
        role="citizen",
        preferences="{}",
        created_at=datetime.now(timezone.utc),
        last_login=datetime.now(timezone.utc),
    )
    check("User model: valid data accepted", u.role == "citizen")
except Exception as e:
    check("User model: valid data accepted", False, str(e))


# ── 2. User model: invalid role raises ValueError ─────────────────────────────
try:
    from app.models.user import User

    u2 = User()
    u2.role = "invalid_role"   # triggers @validates
    check("User model: invalid role raises ValueError", False, "No error was raised")
except ValueError as e:
    check("User model: invalid role raises ValueError", True, str(e))
except Exception as e:
    check("User model: invalid role raises ValueError", False, f"Wrong exception type: {type(e).__name__}: {e}")


# ── 3. auth_service functions are importable ──────────────────────────────────
try:
    from app.services.auth_service import (
        get_user_by_uid,
        update_last_login,
        create_user,
        sync_user,
    )
    check("auth_service: all functions importable", True)
except ImportError as e:
    check("auth_service: all functions importable", False, str(e))


# ── 4. verify_firebase_token: raises 401 with no credentials ─────────────────
try:
    from fastapi import HTTPException
    from app.middleware.auth import verify_firebase_token

    try:
        verify_firebase_token(credentials=None)
        check("Middleware: no token -> 401", False, "No exception raised")
    except HTTPException as e:
        check("Middleware: no token -> 401", e.status_code == 401, f"status={e.status_code}")
except Exception as e:
    check("Middleware: no token -> 401", False, str(e))


# ── 5. verify_firebase_token: raises 401 with invalid token ──────────────────
try:
    from fastapi import HTTPException
    from fastapi.security import HTTPAuthorizationCredentials
    from app.middleware.auth import verify_firebase_token

    fake = HTTPAuthorizationCredentials(scheme="Bearer", credentials="not.a.real.token")
    try:
        verify_firebase_token(credentials=fake)
        check("Middleware: invalid token -> 401", False, "No exception raised")
    except HTTPException as e:
        check(
            "Middleware: invalid token -> 401",
            e.status_code == 401,
            f"status={e.status_code}",
        )
except Exception as e:
    check("Middleware: invalid token -> 401", False, str(e))


# ── 6. SQLite DB: users table and columns exist ───────────────────────────────
try:
    from sqlalchemy import create_engine
    from sqlalchemy import inspect as sa_inspect

    db_path = os.path.join(BACKEND_DIR, "nyaay.db")
    engine = create_engine(f"sqlite:///{db_path}")
    insp = sa_inspect(engine)
    tables = insp.get_table_names()

    if "users" not in tables:
        check("SQLite: users table exists", False, f"Tables found: {tables}")
    else:
        cols = {c["name"]: c for c in insp.get_columns("users")}
        expected = {"firebase_uid", "email", "name", "role", "preferences", "created_at", "last_login"}
        missing = expected - set(cols.keys())

        check("SQLite: users table exists", True, f"Tables: {tables}")
        check(
            "SQLite: all expected columns present",
            not missing,
            f"Missing: {missing}" if missing else str(sorted(cols.keys())),
        )
        check(
            "SQLite: created_at is DATETIME",
            "DATETIME" in str(cols["created_at"]["type"]).upper(),
            str(cols["created_at"]["type"]),
        )
        check(
            "SQLite: last_login is DATETIME",
            "DATETIME" in str(cols["last_login"]["type"]).upper(),
            str(cols["last_login"]["type"]),
        )
except Exception as e:
    check("SQLite: users table exists", False, str(e))


# ── Summary ───────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
passed = sum(1 for _, ok, _ in results if ok)
failed = sum(1 for _, ok, _ in results if not ok)
print(f"Results: {passed} passed, {failed} failed out of {len(results)} checks")
if failed:
    sys.exit(1)
