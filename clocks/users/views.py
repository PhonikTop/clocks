from django.shortcuts import get_object_or_404
from meetings.models import Session
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rooms.models import Room

from .models import User
from .serializers import UserSerializer


@api_view(["POST"])
def join_room(request: Request) -> Response:
    """
    Присоединение пользователя к комнате.
    """
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

    # Получение комнаты
    room: Room = get_object_or_404(Room, id=room_id)

    # Обновление или создание пользователя
    user: User = User.objects.create_user(
        nickname=nickname,
        room=room,
        is_observer=role == "observer",
        state="waiting",
    )

    # Получение или создание активной сессии для комнаты
    session: Session = room.current_session
    if session is None:
        session = Session.objects.create(room=room, task_name="Default Task")
        room.current_session = session
        room.save()

    # Возврат данных пользователя и идентификатора сессии
    serializer = UserSerializer(user)
    return Response(
        {"user": serializer.data, "session_id": session.id}, status=status.HTTP_200_OK
    )


@api_view(["GET"])
def get_current_user(request: Request) -> Response:
    """
    Получение информации о текущем пользователе.
    """
    user: User = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)
