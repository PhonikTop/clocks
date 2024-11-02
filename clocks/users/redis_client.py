from django.core.cache import cache

DEFAULT_TOKEN_TTL = 60 * 60 * 24 * 5  # 5 days


def save_new_client_to_cache(token, nickname: str, role: str, ttl: int = DEFAULT_TOKEN_TTL) -> None:
    """
    Сохранение данных клиента в кэш с использованием token.
    """
    cache.set(token, {"nickname": nickname, "role": role}, ttl)


def check_token_in_cache(token: str) -> bool:
    """
    Проверка на существование записи в кэше.
    """
    return bool(cache.ttl(token))


def get_client_data_by_token(token: str) -> dict[str, str]:
    """
    Получение данных клиента (никнейм и роль) по токену из кэша.
    """
    return cache.get(token, {})
