from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from cryptography.fernet import Fernet, InvalidToken
from settings.settings import CRYPT_KEY

fernet = Fernet(CRYPT_KEY)


def cookie_encrypt(token: str) -> str:
    try:
        return fernet.encrypt(token.encode()).decode()
    except InvalidToken:
        return None


def cookie_decrypt(encrypted_data: str) -> str:
    try:
        return fernet.decrypt(encrypted_data.encode()).decode()
    except InvalidToken:
        return None


def send_to_room_group(room_id, message) -> None:
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"room_{room_id}",
        message
    )
