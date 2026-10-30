from datetime import datetime
from pydantic import BaseModel, Field


class UserSyncRequest(BaseModel):
    """
    Request schema to synchronize user role and name.
    """
    name: str = Field(..., min_length=1, description="Display name of the user")
    role: str = Field(..., description="Role chosen by the user: citizen, student, or lawyer")


class UserResponse(BaseModel):
    """
    Response schema representing a synchronized user profile.
    """
    firebase_uid: str
    email: str
    name: str
    role: str
    preferences: str
    created_at: datetime
    last_login: datetime

    class Config:
        from_attributes = True
