from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


class UserPublic(BaseModel):
    """Safe public view — no email, no password."""

    id: int
    username: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserResponse(UserPublic):
    """Full view returned to the authenticated owner."""

    email: str
    is_active: bool
    is_verified: bool

    model_config = {"from_attributes": True}


class UserStats(BaseModel):
    followers_count: int
    following_count: int
    posts_count: int
