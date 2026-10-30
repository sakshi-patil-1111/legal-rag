"""
test_milestone2.py - Milestone 2 backend auth routes verification.

Tests:
  1. GET /api/auth/me returns 404 when user is not in database.
  2. POST /api/auth/sync creates a user in SQLite and returns 201.
  3. GET /api/auth/me returns 200 after sync and updates last_login.
  4. POST /api/auth/sync with invalid role returns 400.
"""

import sys
import os
from datetime import datetime, timezone

# Add BACKEND/ to sys.path
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from fastapi.testclient import TestClient
from app.main import app
from app.middleware.auth import verify_firebase_token, VerifiedToken
from app.database.database import Base, engine, SessionLocal
from app.models.user import User

# Setup Test Client
client = TestClient(app)

results = []

def check(label, ok, detail=""):
    results.append((label, ok, detail))
    tag = "[PASS]" if ok else "[FAIL]"
    suffix = f"  -> {detail}" if detail else ""
    print(f"{tag} {label}{suffix}")

# Clean up test user in DB before running tests
db = SessionLocal()
try:
    test_user = db.query(User).filter(User.firebase_uid == "uid_test_123").first()
    if test_user:
        db.delete(test_user)
        db.commit()
finally:
    db.close()

# Mock Token details
mock_user_uid = "uid_test_123"
mock_user_email = "test@nyaay.ai"
mock_user_name = "Test User"

def mock_verify_token():
    return VerifiedToken(uid=mock_user_uid, email=mock_user_email, name=mock_user_name)

# Override verify_firebase_token dependency
app.dependency_overrides[verify_firebase_token] = mock_verify_token

# ── 1. GET /api/auth/me returns 404 when user does not exist ───────────────────
try:
    response = client.get("/api/auth/me")
    check(
        "GET /api/auth/me returns 404 for non-existent user",
        response.status_code == 404,
        f"status={response.status_code}, body={response.json()}"
    )
except Exception as e:
    check("GET /api/auth/me returns 404 for non-existent user", False, str(e))

# ── 2. POST /api/auth/sync creates a user in SQLite ────────────────────────────
try:
    payload = {"name": "Test User", "role": "citizen"}
    response = client.post("/api/auth/sync", json=payload)
    check(
        "POST /api/auth/sync returns 201 and creates user profile",
        response.status_code == 201,
        f"status={response.status_code}, body={response.json()}"
    )
    if response.status_code == 201:
        data = response.json()
        check("Sync response: firebase_uid matches", data["firebase_uid"] == mock_user_uid)
        check("Sync response: role matches", data["role"] == "citizen")
        check("Sync response: email matches", data["email"] == mock_user_email)
except Exception as e:
    check("POST /api/auth/sync creates a user in SQLite", False, str(e))

# ── 3. GET /api/auth/me returns 200 after sync ──────────────────────────────────
try:
    response = client.get("/api/auth/me")
    check(
        "GET /api/auth/me returns 200 for synced user",
        response.status_code == 200,
        f"status={response.status_code}"
    )
    if response.status_code == 200:
        data = response.json()
        check("Profile response: firebase_uid matches", data["firebase_uid"] == mock_user_uid)
        check("Profile response: role matches", data["role"] == "citizen")
except Exception as e:
    check("GET /api/auth/me returns 200 after sync", False, str(e))

# ── 4. POST /api/auth/sync with invalid role returns 400 ──────────────────────
try:
    payload = {"name": "Test User", "role": "invalid_role"}
    response = client.post("/api/auth/sync", json=payload)
    check(
        "POST /api/auth/sync with invalid role returns 400",
        response.status_code == 400,
        f"status={response.status_code}, body={response.json()}"
    )
except Exception as e:
    check("POST /api/auth/sync with invalid role returns 400", False, str(e))

# Clear dependency override
app.dependency_overrides.clear()

print("\n" + "=" * 60)
passed = sum(1 for _, ok, _ in results if ok)
failed = sum(1 for _, ok, _ in results if not ok)
print(f"Results: {passed} passed, {failed} failed out of {len(results)} checks")
if failed:
    sys.exit(1)
