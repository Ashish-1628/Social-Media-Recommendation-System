from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.database import get_db
from app.models.user import User
from app.repositories.like_repository import LikeRepository
from app.repositories.user_repository import UserRepository
from app.schemas.post import PostResponse
from app.schemas.recommendation import PostRecommendation, UserRecommendation
from app.schemas.user import UserPublic
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


def _post_to_response(post, like_repo: LikeRepository, current_user_id: int) -> PostResponse:
    return PostResponse(
        id=post.id,
        content=post.content,
        image_url=post.image_url,
        author_id=post.author_id,
        author=UserPublic.model_validate(post.author) if post.author else None,
        likes_count=like_repo.get_likes_count(post.id),
        comments_count=len(post.comments),
        is_liked=like_repo.is_liked(current_user_id, post.id),
        created_at=post.created_at,
        updated_at=post.updated_at,
    )


@router.get("/users", response_model=List[UserRecommendation])
def recommend_users(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Recommend users to follow.
    Combines Friend-of-Friend (BFS) + Collaborative Filtering (Jaccard).
    """
    svc = RecommendationService(db)
    raw = svc.get_user_recommendations(current_user.id, limit)

    user_repo = UserRepository(db)
    results: List[UserRecommendation] = []
    for item in raw:
        user = user_repo.get_by_id(item["user_id"])
        if user:
            results.append(
                UserRecommendation(
                    user=UserPublic.model_validate(user),
                    score=round(item["score"], 4),
                    reason=item["reason"],
                    mutual_connections=item.get("mutual_connections", 0),
                )
            )
    return results


@router.get("/posts", response_model=List[PostRecommendation])
def recommend_posts(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Recommend posts.
    Combines Content-Based (tag matching) + Trending (time-decayed engagement).
    """
    svc = RecommendationService(db)
    raw = svc.get_post_recommendations(current_user.id, limit)

    like_repo = LikeRepository(db)
    results: List[PostRecommendation] = []
    for item in raw:
        post_resp = _post_to_response(item["post"], like_repo, current_user.id)
        results.append(
            PostRecommendation(
                post=post_resp,
                score=round(item["score"], 4),
                reason=item["reason"],
            )
        )
    return results


@router.get("/trending", response_model=List[PostResponse])
def get_trending(
    hours: int = Query(24, ge=1, le=168, description="Look-back window in hours"),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Trending posts ranked by time-decayed engagement score."""
    svc = RecommendationService(db)
    trending = svc.get_trending(hours, limit)

    like_repo = LikeRepository(db)
    return [_post_to_response(item["post"], like_repo, current_user.id) for item in trending]
