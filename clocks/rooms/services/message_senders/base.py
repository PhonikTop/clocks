from abc import ABC, abstractmethod


class MessageSender(ABC):
    @abstractmethod
    def send(self, group_name: str, message: dict) -> None:
        """
        Отправляет сообщение в указанную группу.

        Args:
            group_name (str): Имя группы.
            message (dict): Сообщение, которое нужно отправить.
        """
        pass
