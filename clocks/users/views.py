from api.api_utils import send_to_room_group
from api.authentication import SessionIDAuthentication
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
    authentication_classes = [SessionIDAuthentication]
    serializer_class = UserInputSerializer
    queryset = Room.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user

        nickname, role = serializer.validated_data["nickname"], serializer.validated_data["role"]
        user_uuid = user["uuid"]

        room = self.get_object()

        current_meeting = Meeting.objects.filter(room_id=room.id, active=True).first()
        if not current_meeting:
            raise ValidationError({"error": "No active meeting in the room"})

        room_cache = RoomCacheManager(room.id)

        if room_cache.get_user(user_uuid):
            raise ValidationError({"error": "User already exists in the room"})

        room_cache.add_user(user_uuid, role, nickname)

        send_to_room_group(
            room.id,
            {
                "type": "user_joined",
                "user": nickname,
                "role": role,
            }
        )

        return Response({"nickname": nickname, "role": role}, status=status.HTTP_200_OK)
