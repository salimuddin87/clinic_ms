# app/cache.py
import redis
import os
import json
from typing import Optional, Dict
from app.logger_config import get_logger

logger = get_logger("clinic.cache")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "10"))

try:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
    redis_client.ping()
    logger.info("Connected to Redis")
except Exception as e:
    logger.warning("Redis unavailable: %s", e)
    redis_client = None

CACHE_TTL = 300  # 5 minutes
SESSION_TTL = 86400  # 24 hours


class Cache:
    def __init__(self, client):
        self.client = client

    def get(self, key: str) -> Optional[str]:
        if not self.client:
            return None
        try:
            v = self.client.get(key)
            if v:
                logger.info("Cache hit %s", key)
            return v
        except Exception as e:
            logger.error("Cache get error: %s", e)
            return None

    def set(self, key: str, value, ttl: int = CACHE_TTL):
        if not self.client:
            return
        try:
            val = value if isinstance(value, str) else json.dumps(value, default=str)
            self.client.setex(key, ttl, val)
            logger.info("Cache set %s (ttl=%s)", key, ttl)
        except Exception as e:
            logger.error("Cache set error: %s", e)

    def create_session(self, token: str, payload: Dict):
        if not self.client:
            return
        try:
            self.client.hset(f"session:{token}", mapping=payload)
            self.client.expire(f"session:{token}", SESSION_TTL)
        except Exception as e:
            logger.error("Session create error: %s", e)

    def get_session(self, token: str) -> Optional[Dict]:
        if not self.client:
            return None
        try:
            d = self.client.hgetall(f"session:{token}")
            return d if d else None
        except Exception as e:
            logger.error("Session get error: %s", e)
            return None


# instantiate default cache (importable)
cache = Cache(redis_client)
