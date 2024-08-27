from django.shortcuts import get_object_or_404
from meetings.models import Session
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rooms.models import Room

from .redis_client import save_new_client_to_redis


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

    save_new_client_to_redis(nickname, ("testing_cookie"), role)

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


# TODO: Написать функцию получения информации o пользователе по куки
@api_view(["GET"])
def get_current_user(request: Request) -> Response:
    """
    Получение информации о текущем пользователе.
    """
    # user: User = request.user
    # serializer = UserSerializer(user)
    # return Response(serializer.data, status=status.HTTP_200_OK)
    return None
