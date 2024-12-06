from django.core.cache import cache

DEFAULT_TOKEN_TTL = 60 * 60 * 5


def add_vote(meeting_id: int, user_uuid: str, vote: int) -> None:
    """
    Добавляет или обновляет голос пользователя в кеш с указанием TTL.

    Args:
        meeting_id (int): Уникальный идентификатор голосования.
        user_uuid (str): Уникальный идентификатор пользователя (UUID).
        vote (int): Значение голоса (должно быть числом).

    Returns:
        dict: Обновленный словарь с голосами пользователей, где ключи — UUID пользователей, значения — их голоса.
    """

    key = f"meeting_{meeting_id}"
    votes = cache.get(key, {})
    votes[user_uuid] = vote
    cache.set(key, votes, timeout=DEFAULT_TOKEN_TTL)

    return cache.get(key, {})


def get_votes(meeting_id: int) -> dict:
    """
    Получает все голоса для определенного голосования.

    Args:
        meeting_id (int): Уникальный идентификатор голосования.

    Returns:
        dict: Словарь, где ключи — UUID пользователей, значения — их голоса.
              Возвращает пустой словарь, если данных нет.
    """
    key = f"meeting_{meeting_id}"
    return cache.get(key, {})


def delete_votes(meeting_id: int) -> None:
    """
    Удаляет данные голосования из кеша.

    Args:
        meeting_id (int): Уникальный идентификатор голосования.
    """
    key = f"meeting_{meeting_id}"
    cache.delete(key)
