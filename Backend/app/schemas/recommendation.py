from typing import List
# pyrefly: ignore [missing-import]
from pydantic import BaseModel

from app.schemas.user import UserPublic
from app.schemas.post import PostResponse


class UserRecommendation(BaseModel):
    user: UserPublic
    score: float
    reason: str  # e.g. "Friend of Friend", "Similar Interests"
    mutual_connections: int = 0


class PostRecommendation(BaseModel):
    post: PostResponse
    score: float
    reason: str  # e.g. "Matches Your Interests", "Trending"


class RecommendationResponse(BaseModel):
    recommended_users: List[UserRecommendation] = []
    recommended_posts: List[PostRecommendation] = []
