import uuid

from api.services.jwt_service import JWTService
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rooms.models import Room
from rooms.services.message_senders.django_channel import DjangoChannelMessageSender
from rooms.services.room_cache_service import RoomCacheService
from rooms.services.room_message_service import RoomMessageService

from users.enums import UserRole
from users.serializers import (
    KickUserSerializer,
    UserFullInfoSerializer,
    UserInfoSerializer,
)
from users.services.user_session_service import UserSessionService

USER_TAG=["Users"]

@extend_schema(
    operation_id="createUser",
    summary="Присоединение пользователя к комнате.",
    description="Присоединяет пользователя к комнате и отправляет уведомление участникам этой комнаты через WebSocket.",
    auth=[],
    request=UserInfoSerializer,
    responses={
        200: OpenApiTypes.OBJECT,
    },
    examples=[
        OpenApiExample(
            name="JWT-токен пользователя",
            value={
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3V1aWQiOiI0MWQyZWQyYS1hMTlmLTRkMWItYjE1Mi04NmNiYjBhMDlhOTUiLCJleHAiOjI1MzM5MjQ4NDE0OX0.SfmkZ_ngO2JZErPJtVGNPR9kdDEQr1k-0eu0CJ9vuHg"
            },
            summary="JWT токен пользователя",
            response_only=True,
            status_codes=["200"],
        )
    ],
    tags=USER_TAG,
)
class JoinRoomView(GenericAPIView):
    serializer_class = UserInfoSerializer
    queryset = Room.objects.filter(is_active=True)

    def post(self, request, *args, **kwargs):
        room = self.get_object()
        serializer = self.get_serializer(data=request.data, context={"room": room})
        serializer.is_valid(raise_exception=True)

        nickname = serializer.validated_data["nickname"]
        role_str = serializer.validated_data["role"]

        try:
            role = UserRole(role_str)
        except ValueError:
            return Response({"detail": "Не верное значение роли."}, status=status.HTTP_400_BAD_REQUEST)

        user_uuid = str(uuid.uuid4())

        jwt_service = JWTService()
        room_cache_service = RoomCacheService(room.id)
        user_session_service = UserSessionService(jwt_service, room_cache_service)

        token = user_session_service.create_user_session(user_uuid, role, nickname)

        channel_sender = DjangoChannelMessageSender()
        room_message_service = RoomMessageService(room.id, channel_sender, room_cache_service)

        room_message_service.notify_user_joined(user_uuid)

        return Response({"token": token}, status=status.HTTP_200_OK)

@extend_schema(
    operation_id="getUser",
    summary="Получение информации о пользователе",
    description="Получение информации о пользователе на основе JWT токена из заголовка Authorization.",
    auth=[],
    parameters=[
        OpenApiParameter(
            name="Authorization",
            type=str,
            location="header",
            description='JWT токен в формате "Bearer <token>"',
            required=True,
        )
    ],
    responses={
        200: OpenApiResponse(
            description="Данные сессии пользователя успешно получены.",
            response=UserFullInfoSerializer,
        ),
        401: OpenApiResponse(
            description="Ошибка аутентификации. Токен не предоставлен, неправильный формат или недействительный токен.",
        ),
    },
    tags=USER_TAG,
)
class UserInfoView(GenericAPIView):
    queryset = Room.objects.all()

    def get(self, request, *args, **kwargs):

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            raise AuthenticationFailed("Токен не предоставлен")

        if not auth_header.startswith("Bearer "):
            raise AuthenticationFailed("Неверный формат токена")

        token = auth_header.split(" ")[1]

        room = self.get_object()

        jwt_service = JWTService()
        room_cache_service = RoomCacheService(room.id)
        user_session_service = UserSessionService(jwt_service, room_cache_service)
        try:
            user_data = user_session_service.get_user_session_data(token)
        except Exception:
            raise AuthenticationFailed("Token invalid!")

        return Response(user_data, status=status.HTTP_200_OK)

@extend_schema(
    operation_id="kickUser",
    summary="Удаление пользователя из комнаты",
    auth=[],
    parameters=[
        OpenApiParameter(
            name="Authorization",
            type=str,
            location="header",
            description='JWT токен в формате "Bearer <token>"',
            required=True,
        )
    ],
    request=KickUserSerializer,
    responses={
        200: OpenApiResponse(
            description="Пользователь удалён из комнаты",
        ),
        401: OpenApiResponse(
            description="Ошибка аутентификации. Токен не предоставлен, неправильный формат или недействительный токен.",
        ),
    },
    tags=USER_TAG,
)
class UserKickView(GenericAPIView):
    queryset = Room.objects.filter(is_active=True)
    serializer_class = KickUserSerializer

    def post(self, request, *args, **kwargs):
        auth_header = self.request.headers.get("Authorization")
        if not auth_header:
            raise AuthenticationFailed("Токен не предоставлен")

        if not auth_header.startswith("Bearer "):
            raise AuthenticationFailed("Неверный формат токена")

        token = auth_header.split(" ")[1]

        room = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        jwt_service = JWTService()
        room_cache = RoomCacheService(room)
        user_session_service = UserSessionService(jwt_service, room_cache)

        kicker_uuid = user_session_service.get_user_uuid(token)
        kicked_uuid = serializer.validated_data["user_uuid"]

        room_cache_service = RoomCacheService(room.id)

        channel_sender = DjangoChannelMessageSender()
        room_message_service = RoomMessageService(room.id, channel_sender, room_cache_service)

        room_message_service.notify_user_kicked(kicked_uuid, kicker_uuid)

        room_cache_service.remove_user_vote(kicked_uuid)
        room_cache_service.remove_user(kicked_uuid)

        return Response(status=status.HTTP_200_OK)
