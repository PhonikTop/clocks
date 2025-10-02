import datetime
from typing import Dict

import jwt
from django.conf import settings


class JWTService:
    def __init__(self, secret_key: str = settings.SECRET_KEY, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def generate_token(self, user_uuid: str) -> str:
        expiration = datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(hours=5)
        payload = {"user_uuid": user_uuid, "exp": expiration}
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> Dict:
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError:
            raise Exception("Token expired")
        except jwt.InvalidTokenError:
            raise Exception("Invalid token")
