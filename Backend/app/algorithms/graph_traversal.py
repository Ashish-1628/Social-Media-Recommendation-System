"""
Graph Traversal — Friend-of-Friend (FoF) Recommendations
=========================================================
Uses BFS up to `depth` hops on the social follow graph.
Returns users NOT already followed, ranked by number of distinct
paths that lead from the seed user to each candidate (mutual connection count).
"""
from collections import deque
from typing import Dict, List, Set

from sqlalchemy.orm import Session

from app.repositories.follow_repository import FollowRepository


def get_fof_recommendations(
    user_id: int,
    db: Session,
    depth: int = 2,
    limit: int = 20,
) -> List[Dict]:
    """
    BFS from `user_id` up to `depth` hops.

    Returns:
        List of dicts with keys: user_id, score, reason, mutual_connections
    """
    repo = FollowRepository(db)

    direct_following: Set[int] = set(repo.get_following_ids(user_id))
    visited: Set[int] = {user_id} | direct_following

    # Queue entries: (node_id, current_depth)
    queue: deque = deque((uid, 1) for uid in direct_following)

    # Maps candidate → number of paths that reach them
    candidate_scores: Dict[int, int] = {}

    while queue:
        current_id, current_depth = queue.popleft()

        if current_depth >= depth:
            continue  # Don't expand beyond max depth

        for candidate_id in repo.get_following_ids(current_id):
            if candidate_id not in visited:
                candidate_scores[candidate_id] = candidate_scores.get(candidate_id, 0) + 1
                queue.append((candidate_id, current_depth + 1))
            visited.add(candidate_id)

    sorted_candidates = sorted(
        candidate_scores.items(), key=lambda x: x[1], reverse=True
    )

    return [
        {
            "user_id": uid,
            "score": float(score),
            "reason": "Friend of Friend",
            "mutual_connections": score,
        }
        for uid, score in sorted_candidates[:limit]
    ]
