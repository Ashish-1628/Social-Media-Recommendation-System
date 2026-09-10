"""
Redis cache wrapper
====================
Gracefully degrades to a no-op if Redis is not configured or unavailable.
All callers can use get_cache / set_cache / invalidate_cache without
worrying about Redis connectivity.
"""
import json
import logging
from typing import Any, Optional

logger = logging.getLogger("graphconnect.cache")

_redis_client = None
_redis_unavailable = False  # Flip once to avoid repeated connection attempts


def _get_client():
    global _redis_client, _redis_unavailable
    if _redis_unavailable:
        return None
    if _redis_client is not None:
        return _redis_client

    try:
        from app.core.config import get_settings

        settings = get_settings()
        if not settings.REDIS_URL:
            _redis_unavailable = True
            return None

        import redis  # type: ignore

        client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        client.ping()
        _redis_client = client
        logger.info("Redis connected: %s", settings.REDIS_URL)
        return _redis_client
    except Exception as exc:
        logger.warning("Redis unavailable — caching disabled: %s", exc)
        _redis_unavailable = True
        return None


def get_cache(key: str) -> Optional[Any]:
    client = _get_client()
    if not client:
        return None
    try:
        value = client.get(key)
        return json.loads(value) if value is not None else None
    except Exception:
        return None


def set_cache(key: str, value: Any, ttl: int = 300) -> bool:
    client = _get_client()
    if not client:
        return False
    try:
        client.setex(key, ttl, json.dumps(value, default=str))
        return True
    except Exception:
        return False


def invalidate_cache(key: str) -> bool:
    client = _get_client()
    if not client:
        return False
    try:
        client.delete(key)
        return True
    except Exception:
        return False
