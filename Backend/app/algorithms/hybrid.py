"""
Hybrid Recommendation Engine
==============================
Combines multiple algorithm signals into a single ranked list
using configurable weights.

User recommendations:
    hybrid_score = FoF_score × 0.6  +  CF_score × 0.4

Post recommendations:
    hybrid_score = content_score × 0.7  +  trending_score × 0.3

Duplicate candidates across algorithms have their weighted scores
summed and their reason label updated to reflect both signals.
"""
from typing import Dict, List

from sqlalchemy.orm import Session

from app.algorithms.collaborative_filtering import get_collaborative_recommendations
from app.algorithms.content_based import get_content_recommendations
from app.algorithms.graph_traversal import get_fof_recommendations
from app.algorithms.trending import get_trending_posts

# --- Weight Configuration ---
USER_WEIGHTS = {"fof": 0.6, "cf": 0.4}
POST_WEIGHTS = {"content": 0.7, "trending": 0.3}


def get_hybrid_user_recommendations(
    user_id: int,
    db: Session,
    limit: int = 10,
) -> List[Dict]:
    """Merge FoF and Collaborative Filtering user recommendations."""
    fof = get_fof_recommendations(user_id, db, limit=limit * 2)
    cf = get_collaborative_recommendations(user_id, db, limit=limit * 2)

    merged: Dict[int, Dict] = {}

    for item in fof:
        uid = item["user_id"]
        merged[uid] = {
            "user_id": uid,
            "score": item["score"] * USER_WEIGHTS["fof"],
            "reason": item["reason"],
            "mutual_connections": item.get("mutual_connections", 0),
        }

    for item in cf:
        uid = item["user_id"]
        weighted = item["score"] * USER_WEIGHTS["cf"]
        if uid in merged:
            merged[uid]["score"] += weighted
            merged[uid]["reason"] = "Friend of Friend & Similar Interests"
        else:
            merged[uid] = {
                "user_id": uid,
                "score": weighted,
                "reason": item["reason"],
                "mutual_connections": item.get("mutual_connections", 0),
            }

    return sorted(merged.values(), key=lambda x: x["score"], reverse=True)[:limit]


def get_hybrid_post_recommendations(
    user_id: int,
    db: Session,
    limit: int = 20,
) -> List[Dict]:
    """Merge content-based and trending post recommendations."""
    content = get_content_recommendations(user_id, db, limit=limit * 2)
    trending = get_trending_posts(db, exclude_user_id=user_id, limit=limit * 2)

    merged: Dict[int, Dict] = {}

    for item in content:
        post = item["post"]
        merged[post.id] = {
            "post": post,
            "score": item["score"] * POST_WEIGHTS["content"],
            "reason": item["reason"],
        }

    for item in trending:
        post = item["post"]
        weighted = item["score"] * POST_WEIGHTS["trending"]
        if post.id in merged:
            merged[post.id]["score"] += weighted
            merged[post.id]["reason"] = "Trending & Relevant to You"
        else:
            merged[post.id] = {
                "post": post,
                "score": weighted,
                "reason": item["reason"],
            }

    return sorted(merged.values(), key=lambda x: x["score"], reverse=True)[:limit]
