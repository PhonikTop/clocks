import os

import redis

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "watchy_redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True,
)


def save_new_client_to_redis(token, cookie: str, nickname: str, role: str, ttl: int = 432000) -> None:
    """
    Сохранение данных клиента в Redis с учетом token.
    """
    redis_client.hset(token, mapping={"nickname": nickname, "cookie": cookie, "role": role})
    redis_client.expire(token, ttl)


def check_token_in_db(token: str) -> bool:
    """
    Проверка на существование никнейма в базе.
    """
    return redis_client.exists(token) > 0


def get_client_nickname(token: str) -> str:
    """
    Получение никнейма по токену клиента.
    """
    return redis_client.hget(token, "nickname")


def get_client_data_by_cookie(cookie: str) -> tuple[str, str, str]:
    """
    Получение токена, никнейма и роли по cookie.
    """

    keys = redis_client.keys("*")

    for token in keys:
        if redis_client.hget(token, "cookie") == cookie:
            data = redis_client.hmget(token, "nickname", "role")
            return token, data[0], data[1]

    return None, None, None
