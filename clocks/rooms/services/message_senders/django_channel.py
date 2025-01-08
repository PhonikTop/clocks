from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .base import MessageSender


class DjangoChannelMessageSender(MessageSender):
    def send(self, group_name: str, message: dict) -> None:
        """
        Отправляет сообщение в группу через Django Channels.

        Args:
            group_name (str): Имя группы.
            message (dict): Сообщение, которое нужно отправить.
        """
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(group_name, message)
