from pydantic import BaseModel
from datetime import datetime
from app.schemas.user import UserPublic


class FollowResponse(BaseModel):
    message: str
    is_following: bool


class FollowerItem(BaseModel):
    user: UserPublic
    followed_at: datetime

    model_config = {"from_attributes": True}
