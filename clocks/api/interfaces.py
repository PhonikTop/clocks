from abc import ABC, abstractmethod
from typing import Dict, Optional


class IJWTService(ABC):
    @abstractmethod
    def generate_token(self, user_uuid: str) -> str:
        pass

    @abstractmethod
    def decode_token(self, token: str) -> Dict:
        pass


class IRoomCacheService(ABC):
    """
    Интерфейс для работы с кэшем комнаты.
    """

    @abstractmethod
    def add_user(self, uuid: str, role: str, nickname: str, vote: Optional[int] = None) -> None:
        """
        Добавляет пользователя в кэш комнаты.

        :param uuid: UUID пользователя.
        :param role: Роль пользователя.
        :param nickname: Никнейм пользователя.
        :param vote: Голос пользователя (если есть).
        """
        pass

    @abstractmethod
    def get_user(self, user_uuid: str) -> Optional[Dict[str, Optional[str]]]:
        """
        Получает данные пользователя из кэша.

        :param user_uuid: UUID пользователя.
        :return: Словарь с данными пользователя или None, если пользователь не найден.
        """
        pass

    @abstractmethod
    def remove_user(self, user_uuid: str) -> None:
        """
        Удаляет пользователя из кэша.

        :param user_uuid: UUID пользователя.
        """
        pass

    @abstractmethod
    def get_room_users(self) -> Dict[str, Dict[str, str]]:
        """
        Возвращает всех пользователей в комнате с их ролями.

        :return: Словарь с UUID пользователей и их ролями.
        """
        pass

    @abstractmethod
    def set_vote(self, user_uuid: str, vote: str) -> None:
        """
        Устанавливает голос для пользователя.

        :param user_uuid: UUID пользователя.
        :param vote: Значение голоса.
        """
        pass

    @abstractmethod
    def get_votes(self) -> Dict[str, Dict[str, str]]:
        """
        Получает все голоса в комнате.

        :return: Словарь с голосами (UUID пользователя -> данные голоса).
        """
        pass

    @abstractmethod
    def clear_room(self) -> None:
        """
        Очищает все данные комнаты, включая пользователей и голоса.
        """
        pass
