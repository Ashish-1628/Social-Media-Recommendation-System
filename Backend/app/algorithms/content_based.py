"""
Content-Based Filtering
========================
Recommends posts whose tags overlap with the user's interest profile.

Interest profile is built from:
  1. Explicit interests (user_interests table)
  2. Implicit interests inferred from liked posts' tags

Score = matching_tags / max(user_interest_tag_count, 1)
"""
from typing import Dict, List, Set

from sqlalchemy.orm import Session

from app.models.like import Like
from app.models.post import Post
from app.models.tag import PostTag, UserInterest


def _get_user_tag_ids(user_id: int, db: Session) -> Set[int]:
    explicit = {
        row.tag_id
        for row in db.query(UserInterest).filter(UserInterest.user_id == user_id).all()
    }
    liked_ids = [
        r.post_id for r in db.query(Like.post_id).filter(Like.user_id == user_id).all()
    ]
    implicit = (
        {
            row.tag_id
            for row in db.query(PostTag).filter(PostTag.post_id.in_(liked_ids)).all()
        }
        if liked_ids
        else set()
    )
    return explicit | implicit


def get_content_recommendations(
    user_id: int,
    db: Session,
    limit: int = 20,
) -> List[Dict]:
    """
    Returns posts the user hasn't liked yet, ranked by tag overlap.
    """
    user_tag_ids = _get_user_tag_ids(user_id, db)
    if not user_tag_ids:
        return []

    # Posts the user already liked — exclude from recommendations
    liked_ids: Set[int] = {
        r.post_id for r in db.query(Like.post_id).filter(Like.user_id == user_id).all()
    }

    # Find posts tagged with at least one of the user's interest tags
    matching = db.query(PostTag).filter(PostTag.tag_id.in_(user_tag_ids)).all()

    post_match_count: Dict[int, int] = {}
    for pt in matching:
        if pt.post_id not in liked_ids:
            post_match_count[pt.post_id] = post_match_count.get(pt.post_id, 0) + 1

    sorted_posts = sorted(post_match_count.items(), key=lambda x: x[1], reverse=True)

    results: List[Dict] = []
    for post_id, match_count in sorted_posts[:limit * 2]:  # over-fetch to filter author
        post = (
            db.query(Post)
            .filter(Post.id == post_id, Post.author_id != user_id)
            .first()
        )
        if post:
            results.append(
                {
                    "post": post,
                    "score": match_count / max(len(user_tag_ids), 1),
                    "reason": "Matches Your Interests",
                }
            )
        if len(results) >= limit:
            break

    return results
