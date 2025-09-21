from datetime import datetime, timedelta, timezone

from api.services.jwt_service import JWTService
from django.template.context_processors import request
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers, status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.generics import (
    CreateAPIView,
    GenericAPIView,
    ListAPIView,
    RetrieveDestroyAPIView,
)
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from users.serializers import RoomTimerSerializer, UserInfoSerializer
from users.services.user_session_service import UserSessionService

from rooms.models import Room
from rooms.serializers import (
    RoomDetailSerializer,
    RoomNameSerializer,
)
from rooms.services.message_senders.django_channel import DjangoChannelMessageSender
from rooms.services.room_cache_service import RoomCacheService
from rooms.services.room_message_service import RoomMessageService

ROOM_TAG = ["Rooms"]

@extend_schema(
    operation_id="createRoom",
    summary="Создание новой комнаты",
    responses={
        201: RoomNameSerializer,
        400: OpenApiResponse(
            description="Некорректные входные данные",
        ),
        403: OpenApiResponse(
            description="Доступ запрещён",
        ),
    },
    examples=[
        OpenApiExample("Пример запроса", value={"name": "Room A"}, request_only=True),
        OpenApiExample(
            "Пример ответа",
            value={"id": 1, "name": "Room A"},
            response_only=True,
            status_codes=["201"],
        ),
    ],
    tags=ROOM_TAG,
)
class RoomCreateView(CreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = RoomNameSerializer


@extend_schema(
    operation_id="getRoomsList",
    summary="Получение списка доступных комнат",
    auth=[],
    responses={
        200: RoomDetailSerializer(many=True),
    },
    examples=[
        OpenApiExample(
            "Пример ответа",
            value=[
                {"id": 1, "name": "Room A", "active_meeting_id": 42, "is_active": True},
                {
                    "id": 2,
                    "name": "Room B",
                    "active_meeting_id": None,
                    "is_active": True,
                },
            ],
            response_only=True,
            status_codes=["200"],
        )
    ],
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
        operation_id="deleteRoom",
        summary="Удаление комнаты",
        parameters=[
            OpenApiParameter(
                name="id",
                location="path",
                description="ID комнаты",
                type=int,
                examples=[OpenApiExample("Пример", value=1)]
            )
        ],
        responses={
            204: None,
            403: OpenApiResponse(description="Доступ запрещён"),
            404: OpenApiResponse(description="Комната не найдена")
        },
        tags=ROOM_TAG,
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    @extend_schema(
        operation_id="getRoom",
        summary="Получение информации о комнате",
        auth=[],
        parameters=[
            OpenApiParameter(
                name="id",
                location="path",
                description="ID комнаты",
                type=int,
                examples=[OpenApiExample("Пример", value=1)],
            )
        ],
        responses={
            200: RoomDetailSerializer,
            404: OpenApiResponse(description="Комната не найдена"),
        },
        examples=[
            OpenApiExample(
                "Пример ответа",
                value={
                    "id": 1,
                    "name": "Комната переговоров",
                    "active_meeting_id": 42,
                    "is_active": True,
                },
                response_only=True,
                status_codes=["200"],
            )
        ],
        tags=ROOM_TAG,
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

@extend_schema(
    operation_id="getRoomParticipants",
    summary="Получение списка участников комнаты",
    auth=[],
    parameters=[
        OpenApiParameter(
            name="id",
            location="path",
            description="ID комнаты",
            type=int,
            examples=[OpenApiExample("Пример", value=1)],
        )
    ],
    responses={
        200: inline_serializer(
            name="RoomParticipantsResponse",
            fields={
                "participants": serializers.DictField(
                    child=UserInfoSerializer(),
                )
            },
        ),
        404: OpenApiResponse(
            description="Комната не найдена или пуста",
            response=OpenApiTypes.OBJECT,
            examples=[
                OpenApiExample(
                    "Ошибка", value={"detail": "Комната не найдена или нет участников"}
                )
            ],
        ),
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
                        "role": "observer",
                        "nickname": "User2",
                    },
                }
            },
            status_codes=["200"],
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

class SetRoomTimer(GenericAPIView):
    serializer_class = RoomTimerSerializer

    def post(self, request, pk):
        auth_header = self.request.headers.get("Authorization")
        if not auth_header:
            raise AuthenticationFailed("Токен не предоставлен")

        if not auth_header.startswith("Bearer "):
            raise AuthenticationFailed("Неверный формат токена")

        token = auth_header.split(" ")[1]

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        jwt_service = JWTService()
        room_cache = RoomCacheService(pk)
        user_session_service = UserSessionService(jwt_service, room_cache)

        timer_started_user = user_session_service.get_user_uuid(token)

        minutes = serializer.validated_data["minutes"]
        new_timestamp = int((datetime.now(timezone.utc) + timedelta(minutes=minutes)).timestamp())

        channel_sender = DjangoChannelMessageSender()
        room_message_service = RoomMessageService(pk, channel_sender, room_cache)

        room_message_service.notify_room_timer_started(new_timestamp, timer_started_user)

        room_cache.start_room_timer(new_timestamp)

        return Response(status=status.HTTP_200_OK)

class GetRoomTimer(APIView):
    def get(self, request, pk):
        room_cache = RoomCacheService(pk)

        return Response({"timer_end_time": room_cache.get_room_timer()}, status=status.HTTP_200_OK )

class ResetRoomTimer(APIView):
    def delete(self, request, pk):
        auth_header = self.request.headers.get("Authorization")
        if not auth_header:
            raise AuthenticationFailed("Токен не предоставлен")

        if not auth_header.startswith("Bearer "):
            raise AuthenticationFailed("Неверный формат токена")

        token = auth_header.split(" ")[1]

        room_cache = RoomCacheService(pk)

        jwt_service = JWTService()
        user_session_service = UserSessionService(jwt_service, room_cache)

        timer_reset_user = user_session_service.get_user_uuid(token)
        channel_sender = DjangoChannelMessageSender()
        room_message_service = RoomMessageService(pk, channel_sender, room_cache)

        room_cache.reset_room_timer()
        room_message_service.notify_room_timer_reset(timer_reset_user)
        return Response(status=status.HTTP_200_OK)
