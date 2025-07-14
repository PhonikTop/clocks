from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveDestroyAPIView,
)
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from rooms.models import Room
from rooms.serializers import (
    RoomDetailSerializer,
    RoomNameSerializer,
)
from rooms.services.room_cache_service import RoomCacheService

ROOM_TAG = ["Rooms"]

@extend_schema(
    summary="Создание новой комнаты",
    responses={
        201: RoomNameSerializer,
        400: OpenApiResponse(description="Некорректные входные данные"),
        403: OpenApiResponse(description="Не аутентифицирован")
    },
    examples=[
        OpenApiExample(
            "Пример запроса",
            value={"name": "Room A"},
            request_only=True
        )
    ],
    tags=ROOM_TAG,
)
class RoomCreateView(CreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = RoomNameSerializer


@extend_schema(
    summary="Получение списка доступных комнат",
    responses={
        200: RoomDetailSerializer,
    },
    tags=ROOM_TAG,
)
class RoomListView(ListAPIView):
    serializer_class = RoomDetailSerializer
    queryset = Room.objects.filter(is_active=True)


class RoomDetailView(RetrieveDestroyAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomDetailSerializer

    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAdminUser()]
        return [AllowAny()]

    @extend_schema(
        summary="Удаление комнаты (только для администраторов)",
        responses={
            204: None,
            403: OpenApiResponse(description="Не аутентифицирован"),
            404: OpenApiResponse(description="Комната не найдена")
        },
        tags=ROOM_TAG,
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    @extend_schema(
        summary="Получение информации о комнате.",
        responses={
            200: RoomDetailSerializer,
            404: OpenApiResponse(description="Комната не найдена")
        },
        tags=ROOM_TAG,
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

@extend_schema(
    summary="Получение списка участников конкретной комнаты.",
    responses={
        200: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT,
    },
    examples=[
        OpenApiExample(
            "Пример успешного ответа",
            value={
                "participants": {
                    "5e44c567-da6a-42ec-b01f-821b97c211ce": {
                        "role": "voter",
                        "nickname": "User1",
                    },
                    "a0d35278-c4e9-468f-acc9-f032a9eb0cc5": {
                        "role": "voter",
                        "nickname": "User2",
                    },
                    "9399cba1-6257-4398-919e-005d27c482dc": {
                        "role": "voter",
                        "nickname": "User3",
                    },
                    "0cf90a7d-dccd-45f9-9349-f2a9f650ba7f": {
                        "role": "observer",
                        "nickname": "User4",
                    }
                }
            },
            status_codes=["200"]
        ),
        OpenApiExample(
            "Пример ошибки отсутствия комнаты или участников в ней",
            value={"detail": "Комната не найдена или нет участников"},
            status_codes=["404"]
        )
    ],
    tags=ROOM_TAG,
)
class RoomParticipantsView(APIView):
    def get(self, request, pk):
        room_cache = RoomCacheService(pk)
        participants = room_cache.get_room_users()

        if not participants:
            return Response({"detail": "Комната не найдена или нет участников"}, status=404)

        return Response({"participants": participants})
