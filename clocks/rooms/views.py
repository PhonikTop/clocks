from api.api_utils import APIResponseHandler
from meetings.models import Meeting
from meetings.serializers import MeetingSerializer
from rest_framework import status
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveAPIView,
    RetrieveDestroyAPIView,
    get_object_or_404,
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

    def perform_create(self, serializer):
        serializer.save(is_active=True)


class RoomListView(ListAPIView):
    """
    Получение списка доступных комнат.
    """
    serializer_class = RoomSerializer

    def get_queryset(self):
        return Room.objects.all()


class RoomDetailView(RetrieveDestroyAPIView):
    """
    Получение, удаление и управление конкретной комнатой.
    """
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAuthenticated()]
        return [AllowAny()]


class RoomParticipantsView(RetrieveAPIView):
    """
    Получение списка участников конкретной комнаты.
    """
    serializer_class = RoomSerializer
    queryset = Room.objects.all()

    def get_serializer(self, *args, **kwargs):
        kwargs["fields"] = ["users"]
        return super().get_serializer(*args, **kwargs)

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


class RoomHistoryView(ListAPIView):
    """
    Получение истории всех завершенных сессий в комнате.
    """
    serializer_class = MeetingSerializer

    def get_queryset(self):
        return Meeting.objects.filter(room_id=self.kwargs.get("pk"))
