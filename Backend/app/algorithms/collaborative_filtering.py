"""
User-User Collaborative Filtering
===================================
Finds users with similar social patterns using Jaccard similarity
on the union of their follower + following sets.

Jaccard(A, B) = |A ∩ B| / |A ∪ B|

High Jaccard score → similar social neighbourhood → likely to enjoy
the same content / worth recommending to each other.
"""
from typing import Dict, List, Set

from sqlalchemy.orm import Session

from app.repositories.follow_repository import FollowRepository


def jaccard_similarity(set_a: Set[int], set_b: Set[int]) -> float:
    if not set_a and not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


def get_collaborative_recommendations(
    user_id: int,
    db: Session,
    limit: int = 20,
    candidate_pool_size: int = 150,
) -> List[Dict]:
    """
    Returns users not already followed, ranked by Jaccard similarity.
    """
    repo = FollowRepository(db)

    user_following: Set[int] = set(repo.get_following_ids(user_id))
    user_followers: Set[int] = set(repo.get_followers_ids(user_id))
    user_social: Set[int] = user_following | user_followers

    if not user_social:
        return []

    # Collect candidate pool from 2nd-degree connections
    candidates: Set[int] = set()
    for uid in user_social:
        candidates.update(repo.get_following_ids(uid))
        candidates.update(repo.get_followers_ids(uid))

    # Remove self and already-followed accounts
    candidates -= {user_id} | user_following

    scores: List[Dict] = []
    for candidate_id in list(candidates)[:candidate_pool_size]:
        c_following = set(repo.get_following_ids(candidate_id))
        c_followers = set(repo.get_followers_ids(candidate_id))
        c_social = c_following | c_followers

        sim = jaccard_similarity(user_social, c_social)
        if sim > 0:
            scores.append(
                {
                    "user_id": candidate_id,
                    "score": sim,
                    "reason": "Similar Interests",
                    "mutual_connections": len(user_social & c_social),
                }
            )

    scores.sort(key=lambda x: x["score"], reverse=True)
    return scores[:limit]
