from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rooms.models import Room
from meetings.models import Session

from .redis_client import save_new_client_to_redis


class JoinRoomView(APIView):
    """
    Присоединение пользователя к комнате.
    """

    def post(self, request: Request) -> Response:
        nickname: str = request.data.get("nickname")
        room_id: int = request.data.get("room_id")
        role: str = request.data.get("role")

        # Проверка обязательных параметров
        if not nickname or not room_id or not role:
            return Response(
                {"error": "Missing parameters"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Проверка допустимости роли
        if role not in ["observer", "participant"]:
            return Response({"error": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)

        save_new_client_to_redis(nickname, "testing_cookie", role)

        # Получение комнаты
        room: Room = get_object_or_404(Room, id=room_id)

        # Получение или создание активной сессии для комнаты
        session: Session = room.current_session
        if session is None:
            session = Session.objects.create(room=room, task_name="Введите название таска")
            room.current_session = session
            room.save()

        return Response(
            {"user": nickname, "session_id": session.id}, status=status.HTTP_200_OK
        )


class CurrentUserView(APIView):
    """
    Получение информации о текущем пользователе.
    """

    def get(self, request: Request) -> Response:
        # Если реализация метода временно отсутствует:
        return Response({"detail": "Not implemented"}, status=status.HTTP_501_NOT_IMPLEMENTED)

        # Пример, если потребуется восстановить код:
        # user: User = request.user
        # serializer = UserSerializer(user)
        # return Response(serializer.data, status=status.HTTP_200_OK)
