from typing import Optional
from datetime import datetime
from pydantic import BaseModel

from app.schemas.user import UserPublic


class CommentCreate(BaseModel):
    content: str


class CommentResponse(BaseModel):
    id: int
    content: str
    author_id: int
    post_id: int
    author: Optional[UserPublic] = None
    created_at: datetime

    model_config = {"from_attributes": True}
