import os

import redis

# Подключение к Redis
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True,
)


def save_new_client_to_redis(name: str, cookie_key: tuple, role: str, ttl: int = 432000) -> None:
    """Сохранение оригинальной и укороченной ссылки в Redis с учетом cookie_key."""
    redis_client.hset(name, mapping={"cookie": cookie_key, "role": role})
    redis_client.expire(name, ttl)
