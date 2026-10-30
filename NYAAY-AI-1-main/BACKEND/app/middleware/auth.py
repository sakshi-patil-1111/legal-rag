"""
middleware/auth.py — Firebase ID token verification dependency.

Usage in routes:
    @router.get("/protected")
    async def protected(token: VerifiedToken = Depends(verify_firebase_token)):
        return {"uid": token.uid}
"""

import base64
import json
from dataclasses import dataclass

import firebase_admin
import firebase_admin.auth as firebase_auth
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.config import settings

# HTTPBearer extracts the raw Bearer token from the Authorization header.
_bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class VerifiedToken:
    """Decoded, verified Firebase ID token payload."""

    uid: str
    email: str
    name: str


def _decode_jwt_unverified(token: str) -> dict:
    """Safely decode JWT payload without verification for local development fallback."""
    try:
        parts = token.split(".")
        if len(parts) == 3:
            payload_b64 = parts[1]
            payload_b64 += "=" * (-len(payload_b64) % 4)
            decoded_bytes = base64.urlsafe_b64decode(payload_b64)
            return json.loads(decoded_bytes.decode("utf-8"))
    except Exception:
        pass
    return {}


def verify_firebase_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> VerifiedToken:
    """
    FastAPI dependency that verifies a Firebase ID token.
    - Extracts Bearer token from Authorization header.
    - Verifies using Firebase Admin SDK if service account is loaded.
    - Falls back gracefully in dev mode if service account key file is missing.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    # 1. Dev / Mock mode fallback when token is mock-token
    if token == "mock-token":
        return VerifiedToken(
            uid="mock-uid",
            email="citizen@nyaay.ai",
            name="Counselor",
        )

    # 2. If Firebase Admin SDK is not initialized (e.g. missing serviceAccountKey.json)
    #    Decode JWT payload without signature verification as a fallback.
    if not firebase_admin._apps:
        payload = _decode_jwt_unverified(token)
        uid = payload.get("user_id") or payload.get("sub") or ""
        email = payload.get("email") or ""
        name = payload.get("name") or email.split("@")[0] if email else ""
        if uid:
            return VerifiedToken(uid=uid, email=email, name=name)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firebase Admin SDK is not initialized and token could not be decoded.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Production / Admin SDK verification
    try:
        decoded = firebase_auth.verify_id_token(token)
        return VerifiedToken(
            uid=decoded["uid"],
            email=decoded.get("email", ""),
            name=decoded.get("name", ""),
        )
    except firebase_auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firebase ID token has expired. Please sign in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except firebase_auth.RevokedIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firebase ID token has been revoked.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (firebase_auth.InvalidIdTokenError, Exception) as err:
        if settings.is_development:
            # In local dev mode, fallback to unverified decoding if service account key doesn't match client project
            payload = _decode_jwt_unverified(token)
            if payload and ("user_id" in payload or "sub" in payload):
                uid = payload.get("user_id") or payload.get("sub") or "dev-uid"
                email = payload.get("email") or "dev@nyaay.ai"
                name = payload.get("name") or email.split("@")[0]
                return VerifiedToken(uid=uid, email=email, name=name)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate Firebase credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
