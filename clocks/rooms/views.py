from django.shortcuts import get_list_or_404
from meetings.models import Meeting
from meetings.serializers import MeetingHistorySerializer
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveDestroyAPIView,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Room
from .redis_client import RoomCacheManager
from .serializers import (
    RoomDetailSerializer,
    RoomNameSerializer,
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
    queryset = Room.objects.filter(is_active=True)


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


class RoomParticipantsView(APIView):
    """
    Получение списка участников конкретной комнаты.
    """

    def get(self, request, pk):
        room_cache = RoomCacheManager(pk)
        participants = room_cache.get_room_users()

        if not participants:
            return Response({"detail": "Комната не найдена или нет участников"}, status=404)

        return Response({"participants": participants})


class RoomHistoryView(ListAPIView):
    """
    Получение истории всех завершенных сессий в комнате.
    """
    serializer_class = MeetingHistorySerializer

    def get_queryset(self):
        return get_list_or_404(Meeting, room_id=self.kwargs.get("pk"))
