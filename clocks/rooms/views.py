from api.api_utils import APIResponseHandler
from django.shortcuts import get_object_or_404
from meetings.models import Meeting
from meetings.serializers import MeetingSerializer
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Room
from .serializers import RoomSerializer

response = APIResponseHandler()


class RoomCreateView(APIView):
    """
    Создание новой комнаты
    """
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, *args, **kwargs) -> Response:
        serializer = RoomSerializer(data=request.data, fields=["id", "name"])
        if serializer.is_valid():
            room = serializer.save()
            response_serializer = RoomSerializer(instance=room, fields=["id", "name"])
            return response.success_response(msg="Room created", data=response_serializer.data,
                                             response_status=status.HTTP_201_CREATED)
        return response.error_response(msg="Error", data=serializer.errors,
                                       response_status=status.HTTP_400_BAD_REQUEST)


class RoomListView(APIView):
    """
    Получение списка доступных комнат.
    """

    def get(self, request: Request, *args, **kwargs) -> Response:
        rooms = Room.objects.filter(is_active=True)
        serializer = RoomSerializer(instance=rooms, many=True,
                                    fields=["id", "name", "is_active", "users", "current_meeting_id"])
        return response.success_response(msg="Room list", data=serializer.data,
                                         response_status=status.HTTP_200_OK)


class RoomDetailView(APIView):
    """
    Получение, удаление и управление конкретной комнатой.
    """

    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request: Request, room_id: int, *args, **kwargs) -> Response:
        room = get_object_or_404(Room, id=room_id)
        serializer = RoomSerializer(room)
        return response.success_response(msg="Room info", data=serializer.data,
                                         response_status=status.HTTP_200_OK)

    def delete(self, request: Request, room_id: int, *args, **kwargs) -> Response:
        """
        Удаление комнаты.
        """
        room = get_object_or_404(Room, id=room_id)
        room.delete()
        return response.success_response(msg="Room deleted successfully", data=None,
                                         response_status=status.HTTP_204_NO_CONTENT)


class RoomParticipantsView(APIView):
    """
    Получение списка участников конкретной комнаты.
    """

    def get(self, request: Request, room_id: int, *args, **kwargs) -> Response:
        room = get_object_or_404(Room, id=room_id)
        data = [
            {
                "nickname": nickname,
                "role": "observer" if role == "observer" else "voter",
            }
            for user in room.users
            for nickname, role in user.items()
        ]
        return response.success_response(msg="Room participants", data=data,
                                         response_status=status.HTTP_200_OK)


class RoomHistoryView(APIView):
    """
    Получение истории всех завершенных сессий в комнате.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, room_id: int, *args, **kwargs) -> Response:
        room = get_object_or_404(Room, id=room_id)
        meetings = Meeting.objects.filter(room_id=room, active=False)
        serializer = MeetingSerializer(meetings, many=True,
                                       fields=["id", "room_id", "task_name", "votes", "average_score", "active"])
        return response.success_response(msg="Room history", data=serializer.data,
                                         response_status=status.HTTP_200_OK)
