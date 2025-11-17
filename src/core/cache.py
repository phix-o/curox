import json
from typing import Annotated, Any, TypeVar, Generic

import redis

from fastapi import Depends

from src.core.config import settings

# Redis client singleton
_redis_client: redis.Redis | None = None


def get_redis_client() -> redis.Redis:
    """Get or create Redis client"""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            decode_responses=True,
        )
    return _redis_client


T = TypeVar("T")


class CacheManager(Generic[T]):
    """Simple cache manager for Redis operations"""

    def __init__(self, ttl: int = 3600):
        """
        Initialize cache manager

        Args:
            ttl: Time to live in seconds (default: 1 hour)
        """
        self.redis = get_redis_client()
        self.ttl = ttl

    def get(self, key: str) -> T | None:
        """Get value from cache"""
        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error for key {key}: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """Set value in cache"""
        try:
            self.redis.setex(
                key,
                ttl or self.ttl,
                json.dumps(value, default=str),
            )
            return True
        except Exception as e:
            print(f"Cache set error for key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            self.redis.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error for key {key}: {e}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        try:
            keys = self.redis.keys(pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache clear error for pattern {pattern}: {e}")
            return 0



def get_cache_manager() -> CacheManager[Any]:
    return CacheManager[Any]()


CacheDep = Annotated[CacheManager[T], Depends(get_cache_manager)]
