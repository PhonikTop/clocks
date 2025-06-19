from typing import Dict

from django.core.cache import cache


class RoomOnlineTracker:
    _CACHE_PREFIX = "online"
    _DEFAULT_TTL = 60 * 60 * 5
    @classmethod
    def _make_key(cls, room_id: int) -> str:
        return f"{cls._CACHE_PREFIX}:room_{room_id}"

    @classmethod
    def _set_user_status(cls, user_uuid, room_id, status: bool) -> None:
        room_key = cls._make_key(room_id)
        participants: Dict[str, bool] = cache.get(room_key, {})
        participants[user_uuid] = status
        cache.set(room_key, participants, cls._DEFAULT_TTL)

    @classmethod
    def set_user_offline(cls, user_uuid: str, room_id: int) -> None:
        cls._set_user_status(user_uuid, room_id, False)

    @classmethod
    def set_user_online(cls, user_uuid: str, room_id: int) -> None:
        cls._set_user_status(user_uuid, room_id, True)

    @classmethod
    def get_room_participants(cls, room_id: int) -> Dict[str, bool]:
        room_key = cls._make_key(room_id)
        return cache.get(room_key, {})

    @classmethod
    def clean_room_participant(cls, room_id: int) -> None:
        room_key = cls._make_key(room_id)
        with cache.lock(room_key):
            cache.set(room_key, {}, cls._DEFAULT_TTL)

    @classmethod
    def refresh_ttl(cls, room_id: int) -> None:
        room_key = cls._make_key(room_id)
        if cache.has_key(room_key):
            cache.touch(room_key, cls._DEFAULT_TTL)