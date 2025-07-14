import time

from api.services.jwt_service import JWTService
from rooms.services.room_cache_service import RoomCacheService

from users.enums import UserRole


class UserSessionService:
    def __init__(self, jwt_service: JWTService, cache_service: RoomCacheService):
        self.jwt_service = jwt_service
        self.cache_service = cache_service

    def create_user_session(self, user_uuid: str, role: UserRole, nickname: str) -> str:
        self.cache_service.add_user(user_uuid, role, nickname)
        return self.jwt_service.generate_token(user_uuid)

    def get_user_session_data(self, token: str, max_retries: int = 5, delay: float = 0.1) -> dict:
        decoded_data = self.jwt_service.decode_token(token)
        user_uuid = decoded_data["user_uuid"]

        session_data = None
        for _attempt in range(max_retries):
            session_data = self.cache_service.get_user(user_uuid)
            if isinstance(session_data, dict):
                break
            time.sleep(delay)

        if not isinstance(session_data, dict):
            raise Exception(
                f"Session data for token {token} is invalid: {session_data}"
            )

        session_data["user_uuid"] = user_uuid
        return session_data
