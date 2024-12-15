import uuid

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class SessionIDAuthentication(BaseAuthentication):
    """
    Кастомная аутентификация на основе Django Session с поддержкой создания новой сессии.
    """

    def authenticate(self, request):
        session_key = request.COOKIES.get("sessionid")

        if not session_key:
            return self._create_new_session(request)

        session_data = dict(request.session.items())

        if "user_uuid" not in session_data:
            raise AuthenticationFailed("Invalid session")

        user_data = {
            "uuid": session_data["user_uuid"],
        }

        return user_data, None

    def _create_new_session(self, request):
        """
        Создаёт новую сессию для клиента.
        """
        request.session.create()

        user_uuid = str(uuid.uuid4())
        request.session["user_uuid"] = user_uuid

        return {"uuid": user_uuid}, None

    def authenticate_header(self, request):
        return "SessionID"
