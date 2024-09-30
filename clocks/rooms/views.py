from django.shortcuts import get_list_or_404
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveAPIView,
    RetrieveDestroyAPIView,
)
from rest_framework.permissions import AllowAny, IsAuthenticated

from clocks.meetings.models import Meeting
from clocks.meetings.serializers import MeetingHistorySerializer
from clocks.rooms.models import Room
from clocks.rooms.serializers import (
    RoomDetailSerializer,
    RoomNameSerializer,
    RoomParticipantsSerializer,
)


class RoomCreateView(CreateAPIView):
    """
    Создание новой комнаты
    """
    permission_classes = [IsAuthenticated]
    serializer_class = RoomNameSerializer


class RoomListView(ListAPIView):
    """
    Получение списка доступных комнат.
    """
    serializer_class = RoomDetailSerializer
    queryset = Room.objects.all()


class RoomDetailView(RetrieveDestroyAPIView):
    """
    Получение, удаление и управление конкретной комнатой.
    """
    queryset = Room.objects.all()
    serializer_class = RoomDetailSerializer

    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAuthenticated()]
        return [AllowAny()]


class RoomParticipantsView(RetrieveAPIView):
    """
    Получение списка участников конкретной комнаты.
    """
    serializer_class = RoomParticipantsSerializer
    queryset = Room.objects.all()


class RoomHistoryView(ListAPIView):
    """
    Получение истории всех завершенных сессий в комнате.
    """
    serializer_class = MeetingHistorySerializer

    def get_queryset(self):
        return get_list_or_404(Meeting, room_id=self.kwargs.get("pk"))
