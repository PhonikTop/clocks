from datetime import datetime, timezone
from typing import Dict, List, TypedDict
from uuid import UUID

from django.core.cache import cache
from rest_framework.exceptions import ValidationError
from users.enums import UserRole


class UserData(TypedDict):
    role: UserRole
    nickname: str | None

class RoomCacheService:
    """
    Менеджер кэша для управления комнатами, пользователями и голосами.

    Ключи в кэше формируются на основе UUID комнаты и пользователей.
    """

    def __init__(self, room_uuid: str, ttl: int = 60 * 60 * 5):
        """
        Инициализация менеджера кэша для конкретной комнаты.

        :param room_uuid: UUID комнаты.
        :param ttl: Время жизни (в секундах) записей в кэше.
        """
        self.room_key = f"room:{room_uuid}"
        self.users_key = f"{self.room_key}:users"
        self.votes_key = f"{self.room_key}:votes"
        self.timer_key = f"{self.room_key}:timer"
        self.ttl = ttl

    def _get_user_key(self, uuid: str | UUID) -> str:
        return f"user:{uuid}:data"

    def _update_ttl_list(self, keys: List[str]) -> None:
        for key in keys:
            cache.touch(key, timeout=self.ttl)

    def add_user(self, uuid: str | UUID, role: UserRole, nickname: str | None = None) -> None:
        """
        Добавляет пользователя в кэш комнаты.

        :param uuid: UUID пользователя.
        :param role: Роль пользователя.
        :param nickname: Никнейм пользователя.
        """
        user_uuid = str(uuid)
        user_key = self._get_user_key(user_uuid)

        with cache.lock(self.room_key):
            if self._user_exists(user_uuid):
                raise ValueError("User already exists")


            user_data: UserData= {
                "role": role,
                "nickname": nickname,
            }
            cache.set(user_key, user_data, timeout=self.ttl)

            uuids = set(cache.get(self.users_key, []))
            uuids.add(user_uuid)
            cache.set(self.users_key, list(uuids), timeout=self.ttl)

            self._update_ttl_list(list(uuids))

    def _user_exists(self, user_uuid: str) -> bool:
        """
        Проверяет есть пользователь в кеше.

        :param user_uuid: UUID пользователя.
        :return: Словарь с данными пользователя или None, если пользователь не найден.
        """
        user_key = self._get_user_key(user_uuid)
        return cache.get(user_key) is not None

    def transfer_user(self, user_uuid: str | UUID, target_room_uuid: str | int) -> None:
        target_room_uuid = str(target_room_uuid)
        target_service = RoomCacheService(target_room_uuid, ttl=self.ttl)

        user_data: UserData = self.get_user(user_uuid)
        if not user_data:
            raise ValidationError({"error": "User not found in source room"})

        votes = self.get_votes()
        if user_uuid in votes:
            target_service.set_vote(user_uuid, votes[user_uuid]["vote"])
            self.remove_user_vote(user_uuid)

        self.remove_user(user_uuid)

        target_service.add_user(
            uuid=user_uuid,
            role=user_data["role"],
            nickname=user_data["nickname"],
        )

    def get_user(self, user_uuid: str | UUID) -> UserData | None:
        """
        Получает данные пользователя из кэша.

        :param user_uuid: UUID пользователя.
        :return: Словарь с данными пользователя или None, если пользователь не найден.
        """
        user_uuid = str(user_uuid)
        user_key = self._get_user_key(user_uuid)
        return cache.get(user_key)

    def remove_user(self, user_uuid: str | UUID) -> None:
        """
        Удаляет пользователя из кэша.

        :param user_uuid: UUID пользователя.
        """
        user_uuid = str(user_uuid)
        user_key = self._get_user_key(user_uuid)

        uuids = cache.get(self.users_key, [])
        if uuids and user_uuid in uuids:
            uuids.remove(user_uuid)
            cache.set(self.users_key, uuids, timeout=self.ttl)

        cache.delete(user_key)

    def get_room_users(self) -> Dict[str, UserData]:
        """
        Возвращает всех пользователей в комнате с их ролями.

        :return: Словарь с UUID пользователей и их данными.
        """
        uuids = cache.get(self.users_key, [])

        if not uuids:
            return {}

        user_keys = [self._get_user_key(uuid) for uuid in uuids]
        cached_data = cache.get_many(user_keys)

        users_dict = {}
        for uuid in uuids:
            user_key = self._get_user_key(uuid)
            if user_key in cached_data and cached_data[user_key]:
                users_dict[uuid] = cached_data[user_key]
        return users_dict

    def get_users_by_role(self, role: UserRole) -> List[str]:
        """
        Получает список UUID пользователей с определённой ролью.

        :param role: Роль пользователей.
        :return: Список UUID пользователей с указанной ролью.
        """
        all_users = self.get_room_users()
        return [uuid for uuid, user_data in all_users.items() if user_data["role"] == role]

    def set_vote(self, user_uuid: str | UUID, vote: int) -> None:
        """
        Устанавливает голос для пользователя.

        :param user_uuid: UUID пользователя.
        :param vote: Значение голоса.
        :raises ValueError: Если пользователь не найден или не имеет права голосовать.
        """
        user_uuid = str(user_uuid)

        with cache.lock(self.room_key):
            user_data = self.get_user(user_uuid)
            if not user_data:
                raise ValueError("User not found")

            if user_data["role"] != UserRole.VOTER:
                raise ValueError("User is not allowed to vote")

            votes: Dict[str, dict] = cache.get(self.votes_key, {})
            votes[user_uuid] = {
                "nickname": user_data["nickname"],
                "vote": vote
            }
            cache.set(self.votes_key, votes, timeout=self.ttl)

    def remove_user_vote(self, user_uuid: str | UUID) -> None:
        """
        Удаляет голос конкретного пользователя.

        :param user_uuid: UUID пользователя.
        :raises ValueError: Если пользователь не найден.
        """
        user_uuid = str(user_uuid)

        user_data = self.get_user(user_uuid)
        if not user_data:
            raise ValueError("User not found")

        votes: Dict[str, dict] = cache.get(self.votes_key, {})
        if user_uuid in votes:
            del votes[user_uuid]
            cache.set(self.votes_key, votes, timeout=self.ttl)

    def get_votes(self) -> Dict[str, dict]:
        """
        Получает все голоса в комнате.

        :return: Словарь с голосами (UUID пользователя -> данные голоса).
        """
        return cache.get(self.votes_key, {})

    def clear_votes(self) -> None:
        """
        Очищает все голоса в комнате.
        """
        cache.delete(self.votes_key)

    def clear_room(self) -> None:
        """
        Полностью очищает данные комнаты, включая пользователей и голоса.
        """
        with cache.lock(self.room_key):
            uuids = cache.get(self.users_key, [])
            for user_uuid in uuids:
                cache.delete(f"user:{user_uuid}:data")
            cache.delete(self.users_key)
            cache.delete(self.votes_key)

    def start_room_timer(self, end_time: float) -> None:
        if self.get_room_timer():
            raise ValueError("Timer exists")

        if end_time <= datetime.now(timezone.utc).timestamp():
            raise ValueError("End time is invalid")

        cache.set(self.timer_key, end_time, end_time - datetime.now(timezone.utc).timestamp())

    def get_room_timer(self) -> float | None:
        return cache.get(self.timer_key)

    def reset_room_timer(self) -> None:
        cache.delete(self.timer_key)
