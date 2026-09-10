from typing import List

from sqlalchemy.orm import Session

from app.algorithms.hybrid import get_hybrid_post_recommendations, get_hybrid_user_recommendations
from app.repositories.post_repository import PostRepository
from app.utils.cache import get_cache, set_cache


class RecommendationService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_recommendations(self, user_id: int, limit: int = 10) -> list:
        cache_key = f"rec:users:{user_id}"
        cached = get_cache(cache_key)
        if cached is not None:
            return cached

        results = get_hybrid_user_recommendations(user_id, self.db, limit)
        # Results contain ORM objects — not directly JSON-serialisable for Redis;
        # we only cache the lightweight scalar dicts (user_id, score, reason)
        cacheable = [
            {k: v for k, v in r.items() if k != "post"}
            for r in results
        ]
        set_cache(cache_key, cacheable, ttl=300)
        return results

    def get_post_recommendations(self, user_id: int, limit: int = 20) -> list:
        cache_key = f"rec:posts:{user_id}"
        # Post recs contain ORM objects — skip Redis caching for them
        return get_hybrid_post_recommendations(user_id, self.db, limit)

    def get_trending(self, hours: int = 24, limit: int = 20) -> list:
        repo = PostRepository(self.db)
        return repo.get_trending(hours, limit)
