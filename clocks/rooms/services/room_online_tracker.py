from typing import Dict

from django.core.cache import cache
from rooms.services.message_senders.django_channel import DjangoChannelMessageSender
from rooms.services.room_cache_service import RoomCacheService
from rooms.services.room_message_service import RoomMessageService


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
        message_sender = DjangoChannelMessageSender()
        room_cache_service = RoomCacheService(room_id)
        room_message_service = RoomMessageService(room_id, message_sender, room_cache_service )

        room_cache_service.transfer_user(user_uuid, f"{room_id}_offline")
        cls._set_user_status(user_uuid, room_id, False)
        room_message_service.notify_user_offline(user_uuid)

    @classmethod
    def set_user_online(cls, user_uuid: str, room_id: int) -> None:
        message_sender = DjangoChannelMessageSender()
        room_cache_service = RoomCacheService(room_id)
        room_message_service = RoomMessageService(room_id, message_sender, room_cache_service )
        room_offline_cache_service = RoomCacheService(f"{room_id}_offline")

        if room_offline_cache_service.get_user(user_uuid) is not None:
            room_offline_cache_service.transfer_user(user_uuid, room_id)

        cls._set_user_status(user_uuid, room_id, True)
        room_message_service.notify_user_online(user_uuid)

    @classmethod
    def get_room_participants(cls, room_id: int) -> Dict[str, bool]:
        room_key = cls._make_key(room_id)
        return cache.get(room_key, {})

    @classmethod
    def clean_room_offline_participants(cls, room_id: int) -> None:
        offline_room_cache_service = RoomCacheService(f"{room_id}_offline")
        room_key = cls._make_key(room_id)
        offline_room_cache_service.clear_room()
        cache.set(room_key, {}, cls._DEFAULT_TTL)

    @classmethod
    def refresh_ttl(cls, room_id: int) -> None:
        room_key = cls._make_key(room_id)
        if cache.has_key(room_key):
            cache.touch(room_key, cls._DEFAULT_TTL)
