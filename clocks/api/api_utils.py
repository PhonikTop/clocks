from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def send_user_joined_message_to_group(room_id, nickname, role):
    """
    Отправляет сообщение о присоединении нового участника в группу каналов по идентификатору комнаты.

    Args:
        room_id (str/int): Идентификатор комнаты для отправки сообщения.
        nickname (str): Никнейм участника.
        role (str): Роль участника.
    """
    send_to_room_group(
        room_id,
        {
            "type": "user_joined",
            "user": nickname,
            "role": role,
        }
    )


def send_to_room_group(room_id, message) -> None:
    """
    Отправляет сообщение в группу каналов по идентификатору комнаты.

    Args:
        room_id (str/int): Идентификатор комнаты для отправки сообщения.
        message (dict): Сообщение, которое нужно отправить в группу.
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"room_{room_id}",
        message
    )
