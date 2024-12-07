from django.core.cache import cache

DEFAULT_TOKEN_TTL = 60 * 60 * 5


def add_room_participant(room_id: int, user_uuid: str, role: str) -> None:
    """
    Добавляет или обновляет данные пользователя в кеш с указанием TTL.

    Args:
        room_id (int): Уникальный идентификатор комнаты.
        user_uuid (str): Уникальный идентификатор пользователя (UUID).
        role (str): Роль пользователя.

    Returns:
        dict: Обновленный словарь с пользователями, где ключи — UUID пользователей, значения — их роли.
    """
    key = f"room_{room_id}"
    participants = cache.get(key, {})
    participants[user_uuid] = role
    cache.set(key, participants, timeout=DEFAULT_TOKEN_TTL)

    return cache.get(key, {})


def get_room_participants(room_id: int) -> dict:
    """
    Получает все голоса для определенного голосования.

    Args:
        room_id (int): Уникальный идентификатор голосования.

    Returns:
        dict: Словарь, где ключи — UUID пользователей, значения — их роли.
              Возвращает пустой словарь, если данных нет.
    """
    key = f"room_{room_id}"
    return cache.get(key, {})


def clear_room_participants(room_id: int) -> None:
    """
    Удаляет данные участников комнаты из кеша.

    Args:
        room_id (int): Уникальный идентификатор голосования.
    """
    key = f"room_{room_id}"
    cache.delete(key)


def delete_participant(room_id: int, user_uuid: str) -> None:
    """
    Удаляет данные конкретного пользователя из кеша.

    Args:
        room_id (int): Уникальный идентификатор комнаты.
        user_uuid (str): Уникальный идентификатор пользователя (UUID).
    """
    key = f"room_{room_id}"
    participants = cache.get(key, {})
    if user_uuid in participants:
        del participants[user_uuid]
        cache.set(key, participants, timeout=DEFAULT_TOKEN_TTL)


def get_participant_role(room_id: int, user_uuid: str) -> str:
    """
    Возвращает роль определенного участника комнаты.

    Args:
        room_id (int): Уникальный идентификатор комнаты.
        user_uuid (str): Уникальный идентификатор пользователя (UUID).

    Returns:
        str: Роль пользователя. Возвращает пустую строку, если пользователь отсутствует.
    """
    key = f"room_{room_id}"
    participants = cache.get(key, {})
    return participants.get(user_uuid, "")
