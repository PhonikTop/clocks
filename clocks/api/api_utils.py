from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from cryptography.fernet import Fernet, InvalidToken
from settings.settings import CRYPT_KEY

# Глобальная переменная для Fernet
fernet = Fernet(CRYPT_KEY)


def cookie_encrypt(token: str) -> str:
    """
    Шифрует строку токена с использованием Fernet.

    Args:
        token (str): Токен для шифрования.

    Returns:
        str: Зашифрованная строка или None в случае ошибки.
    """
    try:
        return fernet.encrypt(token.encode()).decode()
    except InvalidToken:
        return None


def cookie_decrypt(encrypted_data: str) -> str:
    """
    Расшифровывает зашифрованную строку с использованием Fernet.

    Args:
        encrypted_data (str): Зашифрованные данные для расшифровки.

    Returns:
        str: Расшифрованная строка или None в случае ошибки.
    """
    try:
        return fernet.decrypt(encrypted_data.encode()).decode()
    except InvalidToken:
        return None


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
