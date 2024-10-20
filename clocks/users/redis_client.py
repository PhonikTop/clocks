from django.core.cache import cache


def save_new_client_to_cache(self, token, nickname: str, role: str, ttl: int = 432000) -> None:
    """
    Сохранение данных клиента в кэш с использованием token.
    """
    cache.set(token, {"nickname": nickname, "role": role}, ttl)


def check_token_in_cache(self, token: str) -> bool:
    """
    Проверка на существование записи в кэше.
    """
    return cache.get(token) is not None


def get_client_data_by_token(self, token: str) -> dict[str, str]:
    """
    Получение данных клиента (никнейм и роль) по токену из кэша.
    """
    return cache.get(token, {})
