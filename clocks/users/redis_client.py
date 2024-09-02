import os

import redis

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True,
)


def save_new_client_to_redis(cookie_key: str, nickname: str, role: str, ttl: int = 432000) -> None:
    """Сохранение оригинальной и укороченной ссылки в Redis с учетом cookie_key."""
    redis_client.hset(cookie_key, mapping={"nickname": nickname, "role": role})
    print(cookie_key, nickname, role)
    redis_client.expire(cookie_key, ttl)


def check_nickname_in_db(cookie_key: str) -> bool:
    """
    Проверка на существование никнейма в базе.
    """
    return redis_client.exists(cookie_key) > 0
