import uuid

from api.api_utils import cookie_decrypt, cookie_encrypt, send_to_room_group
from meetings.models import Meeting
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rooms.models import Room
from rooms.redis_client import RoomCacheManager

from .serializers import UserInputSerializer


class JoinRoomView(GenericAPIView):
    """
    Присоединение пользователя к комнате.
    """
    serializer_class = UserInputSerializer
    queryset = Room.objects.all()

    def post(self, request, *args, **kwargs):
        room = self.get_object()
        room_cache = RoomCacheManager(room.id)

        current_meeting = Meeting.objects.filter(room=room, active=True).first()

        if not current_meeting:
            raise ValidationError({"error": "No active meeting in the room"})

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        nickname, role = serializer.validated_data["nickname"], serializer.validated_data["role"]
        cookie = self.request.COOKIES.get("user")
        try:
            token = cookie_decrypt(cookie)
        except AttributeError:
            token = str(uuid.uuid4())

        response = Response(serializer.data, status=status.HTTP_201_CREATED if cookie is None else status.HTTP_200_OK)
        if cookie is None:
            response.set_cookie("user", value=cookie_encrypt(token), max_age=432000)

        if room_cache.get_user(token):
            raise ValidationError({"error": "User exists"})

        room_cache.add_user(token, role, nickname)

        send_to_room_group(
            room.id,
            {
                "type": "user_joined",
                "user": nickname,
                "role": role
            }
        )

        return response
