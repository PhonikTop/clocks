import uuid

from api.services.jwt_service import JWTService
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rooms.models import Room
from rooms.services.message_senders.django_channel import DjangoChannelMessageSender
from rooms.services.room_cache_service import RoomCacheService
from rooms.services.room_message_service import RoomMessageService

from .serializers import UserInputSerializer
from .services.user_session_service import UserSessionService


class JoinRoomView(GenericAPIView):
    """
    Присоединение пользователя к комнате.
    """
    serializer_class = UserInputSerializer
    queryset = Room.objects.all()

    def post(self, request, *args, **kwargs):
        room = self.get_object()
        serializer = self.get_serializer(data=request.data, context={"room": room})
        serializer.is_valid(raise_exception=True)

        nickname, role = serializer.validated_data["nickname"], serializer.validated_data["role"]
        user_uuid = str(uuid.uuid4())

        jwt_service = JWTService()
        room_cache_service = RoomCacheService(room.id)
        user_session_service = UserSessionService(jwt_service, room_cache_service)

        token = user_session_service.create_user_session(user_uuid, role, nickname)

        channel_sender = DjangoChannelMessageSender()
        room_message_service = RoomMessageService(channel_sender)

        room_message_service.notify_user_joined(room.id, user_uuid, nickname, role)

        return Response({"token": token}, status=status.HTTP_200_OK)


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
