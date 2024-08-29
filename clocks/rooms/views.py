from django.shortcuts import get_object_or_404
from meetings.models import Meeting
from meetings.serializers import MeetingSerializer
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Room
from .serializers import RoomSerializer


class RoomCreateView(APIView):
    """
    Создание новой комнаты
    """

    def post(self, request: Request, *args, **kwargs) -> Response:
        name = request.data.get("name", )
        if not name:
            return Response(
                {"error": "Room name is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        room = Room.objects.create(name=name)
        serializer = RoomSerializer(instance=room, fields=["id", "name"])
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RoomListView(APIView):
    """
    Получение списка доступных комнат и создание новой комнаты.
    """

    def get(self, request: Request, *args, **kwargs) -> Response:
        """
        Получение списка активных комнат.
        """
        rooms = Room.objects.filter(is_active=True)
        serializer = RoomSerializer(instance=rooms, many=True,
                                    fields=["id", "name", "is_active", "users", "current_meeting_id"])
        return Response(serializer.data, status=status.HTTP_200_OK)


class RoomDetailView(APIView):
    """
    Получение, удаление и управление конкретной комнатой.
    """

    def get(self, request: Request, room_id: int, *args, **kwargs) -> Response:
        """
        Получение информации о конкретной комнате.
        """
        room = get_object_or_404(Room, id=room_id)
        serializer = RoomSerializer(room)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request: Request, room_id: int, *args, **kwargs) -> Response:
        """
        Удаление комнаты.
        """
        room = get_object_or_404(Room, id=room_id)
        room.delete()
        return Response(
            {"message": "Room deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )


class RoomParticipantsView(APIView):
    """
    Получение списка участников конкретной комнаты.
    """

    def get(self, request: Request, room_id: int, *args, **kwargs) -> Response:
        """
        Получение списка участников комнаты.
        """
        room = get_object_or_404(Room, id=room_id)
        data = [
            {
                "nickname": nickname,
                "role": "observer" if role == "observer" else "voter",
            }
            for user in room.users
            for nickname, role in user.items()
        ]

        return Response(data, status=status.HTTP_200_OK)


class RoomHistoryView(APIView):
    """
    Получение истории всех завершенных сессий в комнате.
    """

    def get(self, request: Request, room_id: int, *args, **kwargs) -> Response:
        """
        Получение истории сессий в комнате.
        """
        room = get_object_or_404(Room, id=room_id)
        meetings = Meeting.objects.filter(room=room, active=False)

        serializer = MeetingSerializer(meetings, many=True,
                                       fields=["id", "room", "task_name", "votes", "average_score", "active"])

        return Response(serializer.data, status=status.HTTP_200_OK)
