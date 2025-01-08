from .message_senders.base import MessageSender


class RoomMessageService:
    def __init__(self, message_sender: MessageSender):
        self.message_sender = message_sender

    def notify_user_joined(self, room_id: int, nickname: str, role: str) -> None:
        """
        Уведомляет о присоединении пользователя к комнате.

        Args:
            room_id (int): Идентификатор комнаты.
            nickname (str): Никнейм пользователя.
            role (str): Роль пользователя.
        """
        group_name = f"room_{room_id}"
        message = {
            "type": "user_joined",
            "user": nickname,
            "role": role,
        }
        self.message_sender.send(group_name, message)
