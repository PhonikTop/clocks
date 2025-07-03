from enum import Enum
from typing import Dict, Optional, Set

from django.core.cache import cache


class KeyType(Enum):
    CHANNEL = "channel"
    ROOM_PARTICIPANTS = "room_participants"


class UserChannelTracker:
    _CACHE_PREFIX = "ws_sessions"
    _DEFAULT_TTL = 60 * 60 * 2

    @classmethod
    def _make_key(cls, key_type: KeyType, identifier: str) -> str:
        return f"{cls._CACHE_PREFIX}:{key_type.value}:{identifier}"

    @classmethod
    def add_participant(cls, channel_name: str, user_uuid: str, room_id: int) -> None:
        chan_key = cls._make_key(KeyType.CHANNEL, channel_name)
        part_key = cls._make_key(KeyType.ROOM_PARTICIPANTS, str(room_id))

        participants: Set[str] = cache.get(part_key, set())

        if channel_name not in participants:
            participants.add(channel_name)
            cache.set(part_key, participants, cls._DEFAULT_TTL)

        cache.set(chan_key, {"user_uuid": user_uuid, "room_id": room_id}, cls._DEFAULT_TTL)

    @classmethod
    def remove_participant(cls, channel_name: str) -> None:
        chan_key = cls._make_key(KeyType.CHANNEL, channel_name)
        data = cache.get(chan_key)
        if not data:
            return

        room_id = data["room_id"]
        part_key = cls._make_key(KeyType.ROOM_PARTICIPANTS, str(room_id))

        participants: Set[str] = cache.get(part_key, set())
        participants.discard(channel_name)
        if participants:
            cache.set(part_key, participants, cls._DEFAULT_TTL)
        else:
            cache.delete(part_key)

        cache.delete(chan_key)

    @classmethod
    def get_participant_info(cls, channel_name: str) -> Optional[Dict[str, str]]:
        chan_key = cls._make_key(KeyType.CHANNEL, channel_name)
        return cache.get(chan_key)

    @classmethod
    def get_room_participants(cls, room_id: int) -> Set[str]:
        part_key = cls._make_key(KeyType.ROOM_PARTICIPANTS, str(room_id))
        return set(cache.get(part_key, set()))

    @classmethod
    def refresh_ttl(cls, channel_name: str) -> None:
        info = cls.get_participant_info(channel_name)
        if not info:
            return
        chan_key = cls._make_key(KeyType.CHANNEL, channel_name)
        part_key = cls._make_key(KeyType.ROOM_PARTICIPANTS, str(info["room_id"]))
        cache.touch(chan_key, cls._DEFAULT_TTL)
        cache.touch(part_key, cls._DEFAULT_TTL)
