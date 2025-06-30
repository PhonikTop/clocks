from typing import Dict, List, Optional
from uuid import UUID

from api.interfaces import IRoomCacheService
from django.core.cache import cache
from rest_framework.exceptions import ValidationError
from users.serializers import UserRoleChoices


class RoomCacheService(IRoomCacheService):
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
        self.ttl = ttl

    def _get_user_key(self, uuid: str | UUID) -> str:
        return f"user:{uuid}:data"

    def add_user(self, uuid: str | UUID, role: UserRoleChoices, nickname: str, vote: Optional[str] = None) -> None:
        """
        Добавляет пользователя в кэш комнаты.

        :param uuid: UUID пользователя.
        :param role: Роль пользователя.
        :param nickname: Никнейм пользователя.
        :param vote: Голос пользователя (если есть).
        """
        user_uuid = str(uuid)
        user_key = self._get_user_key(user_uuid)

        with cache.lock(self.room_key):
            if self._user_exists(user_uuid):
                raise ValidationError({"error": "User already exists in the room"})


            user_data = {
                "role": role,
                "nickname": nickname,
                "vote": vote
            }
            cache.set(user_key, user_data, timeout=self.ttl)

            uuids = set(cache.get(self.users_key, []))
            uuids.add(user_uuid)
            cache.set(self.users_key, list(uuids), timeout=self.ttl)

            if vote is not None:
                votes: Dict[str, dict] = cache.get(self.votes_key, {})
                votes[user_uuid] = {
                    "nickname": nickname,
                    "vote": vote
                }
                cache.set(self.votes_key, votes, timeout=self.ttl)

    def _user_exists(self, user_uuid: str) -> bool:
        """
        Проверяет есть пользователь в кеше.

        :param user_uuid: UUID пользователя.
        :return: Словарь с данными пользователя или None, если пользователь не найден.
        """
        user_key = self._get_user_key(user_uuid)
        return cache.get(user_key) is not None

    def get_user(self, user_uuid: str | UUID) -> Optional[dict]:
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
        vote = self.get_user(user_uuid)["vote"]
        if vote is not None:
            self.remove_user_vote(user_uuid)

        cache.delete(user_key)

        uuids = cache.get(self.users_key, [])
        if uuids and user_uuid in uuids:
            uuids.remove(user_uuid)
            cache.set(self.users_key, uuids, timeout=self.ttl)

    def get_room_users(self) -> Dict[str, dict]:
        """
        Возвращает всех пользователей в комнате с их ролями.

        :return: Словарь с UUID пользователей и их данными.
        """
        uuids = cache.get(self.users_key, [])
        users_dict: Dict[str, dict] = {}
        for uuid in uuids:
            user_data = cache.get(self._get_user_key(str(uuid)))
            if user_data:
                users_dict[uuid] = user_data
        return users_dict

    def get_users_by_role(self, role: UserRoleChoices) -> List[str]:
        """
        Получает список UUID пользователей с определённой ролью.

        :param role: Роль пользователей.
        :return: Список UUID пользователей с указанной ролью.
        """
        all_users = self.get_room_users()
        return [uuid for uuid, user_data in all_users.items() if user_data["role"] == role]

    def set_vote(self, user_uuid: str | UUID, vote: str) -> None:
        """
        Устанавливает голос для пользователя.

        :param user_uuid: UUID пользователя.
        :param vote: Значение голоса.
        :raises ValueError: Если пользователь не найден или не имеет права голосовать.
        """
        user_uuid = str(user_uuid)
        user_key = self._get_user_key(user_uuid)

        with cache.lock(self.room_key):
            user_data = cache.get(user_key)
            if not user_data:
                raise ValueError("User not found")

            if user_data["role"] != "voter":
                raise ValueError("User is not allowed to vote")

            user_data["vote"] = vote
            cache.set(user_key, user_data, timeout=self.ttl)

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
        user_key = self._get_user_key(user_uuid)

        user_data = cache.get(user_key)
        if not user_data:
            raise ValueError("User not found")

        if user_data.get("vote") is None:
            return

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
