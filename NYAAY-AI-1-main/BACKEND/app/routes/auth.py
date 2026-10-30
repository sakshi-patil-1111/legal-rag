from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.middleware.auth import VerifiedToken, verify_firebase_token
from app.schemas.auth import UserResponse, UserSyncRequest
from app.services import auth_service

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    db: Session = Depends(get_db),
    token: VerifiedToken = Depends(verify_firebase_token),
):
    """
    Get the current user's database profile.
    If the user does not exist in SQLite, returns 404 (needs role selection/sync).
    Otherwise, updates last_login and returns user profile.
    """
    user = auth_service.get_user_by_uid(db, token.uid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found in local database."
        )
    
    # Update last login timestamp
    updated_user = auth_service.update_last_login(db, token.uid)
    return updated_user


@router.post("/sync", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def sync_user_profile(
    payload: UserSyncRequest,
    db: Session = Depends(get_db),
    token: VerifiedToken = Depends(verify_firebase_token),
):
    """
    Create or update the user's database profile.
    Saves the user with the specified role and name.
    """
    try:
        user = auth_service.sync_user(
            db=db,
            firebase_uid=token.uid,
            email=token.email,
            name=payload.name,
            role=payload.role,
        )
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
