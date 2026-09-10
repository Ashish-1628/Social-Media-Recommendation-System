"""
Trending Algorithm
===================
Ranks posts by a time-decayed engagement score inspired by
Hacker News ranking:

    score = likes / (hours_since_post + 2) ^ gravity

  - Higher gravity → older posts decay faster
  - The +2 constant prevents division by zero and dampens very
    new posts with no likes from dominating.
"""
import math
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.like import Like
from app.models.post import Post

GRAVITY: float = 1.5


def _time_decay_score(likes: int, hours_old: float, gravity: float = GRAVITY) -> float:
    return likes / math.pow(hours_old + 2, gravity)


def get_trending_posts(
    db: Session,
    hours: int = 48,
    limit: int = 20,
    exclude_user_id: Optional[int] = None,
) -> List[Dict]:
    """
    Returns posts ranked by time-decayed engagement score.

    Args:
        hours: Look-back window in hours.
        exclude_user_id: Optionally exclude posts by a specific user (e.g. self).
    """
    since = datetime.now(timezone.utc) - timedelta(hours=hours)

    query = (
        db.query(Post, func.count(Like.id).label("likes_count"))
        .outerjoin(Like, Post.id == Like.post_id)
        .filter(Post.created_at >= since)
        .group_by(Post.id)
    )
    if exclude_user_id is not None:
        query = query.filter(Post.author_id != exclude_user_id)

    now = datetime.now(timezone.utc)
    scored: List[Dict] = []

    for post, likes_count in query.all():
        created = post.created_at
        if created is not None and created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        hours_old = max((now - created).total_seconds() / 3600, 0) if created else 0
        score = _time_decay_score(likes_count or 0, hours_old)
        scored.append(
            {
                "post": post,
                "score": score,
                "reason": "Trending",
                "likes_count": likes_count or 0,
            }
        )

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:limit]
