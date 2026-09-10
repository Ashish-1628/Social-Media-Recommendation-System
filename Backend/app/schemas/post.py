from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from app.schemas.user import UserPublic


class PostCreate(BaseModel):
    content: str
    image_url: Optional[str] = None
    tags: Optional[List[str]] = []


class PostUpdate(BaseModel):
    content: Optional[str] = None
    image_url: Optional[str] = None


class PostResponse(BaseModel):
    id: int
    content: str
    image_url: Optional[str] = None
    author_id: int
    author: Optional[UserPublic] = None
    likes_count: int = 0
    comments_count: int = 0
    is_liked: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
