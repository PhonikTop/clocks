from cryptography.fernet import Fernet, InvalidToken
from settings.settings import CRYPT_KEY


class Cookies_utils:
    def __init__(self):
        self.key = str(CRYPT_KEY)
        self.fernet = Fernet(self.key)

    def cookie_encrypt(self, token: str) -> str:
        try:
            return self.fernet.encrypt(token.encode()).decode()
        except InvalidToken:
            return None

    def cookie_decrypt(self, encrypted_data) -> str:
        try:
            return self.fernet.decrypt(encrypted_data).decode()
        except InvalidToken:
            return None

