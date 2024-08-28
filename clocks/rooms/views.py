from django.shortcuts import get_object_or_404
from meetings.models import Session
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
        name = request.data.get("name")
        if not name:
            return Response(
                {"error": "Room name is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        room = Room.objects.create(name=name)
        serializer = RoomSerializer(room)
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
        serializer = RoomSerializer(rooms, many=True)
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
                "nickname": list(user.keys())[0],
                "role": "observer" if user[list(user.keys())[0]] == "observer" else "voter",
            }
            for user in room.users  # Предполагается, что room.users — это queryset
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
        sessions = Session.objects.filter(room=room, active=False)
        data = [
            {
                "id": session.id,
                "task_name": session.task_name,
                "average_score": session.average_score,
            }
            for session in sessions
        ]
        return Response(data, status=status.HTTP_200_OK)
