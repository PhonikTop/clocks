from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from .models import Room
from .serializers import RoomSerializer


@api_view(["GET"])
def get_rooms(request: Request) -> Response:
    """
    Получение списка доступных комнат.
    """
    rooms = Room.objects.filter(is_active=True)
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def create_room(request: Request) -> Response:
    """
    Создание новой комнаты.
    """
    name: str = request.data.get("name")

    if not name:
        return Response(
            {"error": "Room name is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    room: Room = Room.objects.create(name=name)
    serializer = RoomSerializer(room)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def get_room(request: Request, room_id: int) -> Response:
    """
    Получение информации о конкретной комнате.
    """
    room: Room = get_object_or_404(Room, id=room_id)
    serializer = RoomSerializer(room)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["DELETE"])
def delete_room(request: Request, room_id: int) -> Response:
    """
    Удаление комнаты.
    """
    room: Room = get_object_or_404(Room, id=room_id)
    room.delete()
    return Response(
        {"message": "Room deleted successfully"}, status=status.HTTP_204_NO_CONTENT
    )


@api_view(["GET"])
def get_room_participants(request: Request, room_id: int) -> Response:
    """
    Получение списка участников комнаты.
    """
    room: Room = get_object_or_404(Room, id=room_id)
    data = [
        {
            "id": user.id,
            "nickname": user.nickname,
            "role": "observer" if user.is_observer else "voter",
            "state": user.state,
        }
        for user in room.users.all()
    ]
    return Response(data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_room_history(request: Request, room_id: int) -> Response:
    from ..meetings.models import Session
    """
    Получение истории всех сессий в комнате.
    """
    room: Room = get_object_or_404(Room, id=room_id)
    sessions = Session.objects.filter(room=room, status="completed")
    data = [
        {
            "id": session.id,
            "task_name": session.task_name,
            "average_score": session.average_score,
        }
        for session in sessions
    ]
    return Response(data, status=status.HTTP_200_OK)
