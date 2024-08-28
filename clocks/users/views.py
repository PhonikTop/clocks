from django.shortcuts import get_object_or_404
from meetings.models import Meeting
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rooms.models import Room

from .redis_client import check_nickname_in_db, save_new_client_to_redis


class JoinRoomView(APIView):
    """
    Присоединение пользователя к комнате.
    """

    def post(self, request: Request) -> Response:
        nickname: str = request.data.get("nickname", )
        room_id: int = request.data.get("room_id", )
        role: str = request.data.get("role", )

        # Проверка обязательных параметров
        if not all([nickname, room_id, role]):
            return Response(
                {"error": "Missing parameters"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Проверка допустимости роли
        if role not in ["observer", "participant"]:
            return Response({"error": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)

        # Проверка наличия пользователя в базе данных
        if not check_nickname_in_db(nickname):
            save_new_client_to_redis(nickname, "testing_cookie", role)

            # Получение комнаты
            room: Room = get_object_or_404(Room, id=room_id)
            room.users.append({nickname: role})
            room.save()
            # Получение или создание активной сессии для комнаты
            meeting: Meeting = room.current_meeting
            if meeting is None:
                meeting = Meeting.objects.create(room=room, task_name="Введите название таска")
                room.current_meeting = meeting
                room.save()

            return Response(
                {"user": nickname, "Meeting": meeting.id}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"detail": "Юзер уже существует"}, status=status.HTTP_200_OK
            )


class CurrentUserView(APIView):
    """
    Получение информации о текущем пользователе.
    """

    def get(self, request: Request) -> Response:
        # Если реализация метода временно отсутствует:
        return Response({"detail": "Not implemented"}, status=status.HTTP_501_NOT_IMPLEMENTED)
