from api.api_utils import APIResponseHandler
from meetings.models import Meeting
from meetings.serializers import MeetingSerializer
from rest_framework import status
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    RetrieveAPIView,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .models import Room
from .serializers import RoomSerializer

response = APIResponseHandler()


class RoomCreateView(CreateAPIView):
    """
    Создание новой комнаты
    """
    permission_classes = [IsAuthenticated]
    serializer_class = RoomSerializer

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data, fields=["id", "name"])
        if serializer.is_valid():
            room = serializer.save()
            response_serializer = self.get_serializer(instance=room, fields=["id", "name"])
            return response.success_response(msg="Room created", data=response_serializer.data,
                                             response_status=status.HTTP_201_CREATED)
        return response.error_response(msg="Error", data=serializer.errors,
                                       response_status=status.HTTP_400_BAD_REQUEST)


class RoomListView(ListAPIView):
    """
    Получение списка доступных комнат.
    """
    serializer_class = RoomSerializer
    lookup_field = "id"

    def get_queryset(self):
        return Room.objects.all()


class RoomDetailView(RetrieveAPIView, DestroyAPIView):
    """
    Получение, удаление и управление конкретной комнатой.
    """
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    lookup_field = "id"

    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAuthenticated()]
        return [AllowAny()]

    def delete(self, request: Request, *args, **kwargs) -> Response:
        room = self.get_object()
        room.delete()
        return response.success_response(msg="Room deleted successfully", data=None,
                                         response_status=status.HTTP_204_NO_CONTENT)


class RoomParticipantsView(RetrieveAPIView):
    """
    Получение списка участников конкретной комнаты.
    """
    serializer_class = RoomSerializer
    lookup_field = "id"

    def get(self, request: Request, *args, **kwargs) -> Response:
        room = self.get_object()
        data = [
            {
                "token": token,
                "role": "observer" if role == "observer" else "voter",
            }
            for user in room.users
            for token, role in user.items()
        ]
        return response.success_response(msg="Room participants", data=data,
                                         response_status=status.HTTP_200_OK)

    def get_object(self):
        return Room.objects.get(id=self.kwargs.get("id"))


class RoomHistoryView(ListAPIView):
    """
    Получение истории всех завершенных сессий в комнате.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = MeetingSerializer
    lookup_field = "id"

    def get_queryset(self):
        room = Room.objects.get(id=self.kwargs.get("id"))
        return Meeting.objects.filter(room=room, active=False)
