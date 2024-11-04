import uuid

from api.api_utils import cookie_decrypt, cookie_encrypt, send_to_room_group
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView, RetrieveAPIView
from rest_framework.response import Response
from rooms.models import Room

from .redis_client import (
    check_token_in_cache,
    get_client_data_by_token,
    save_new_client_to_cache,
)
from .serializers import UserInputSerializer


class JoinRoomView(GenericAPIView):
    """
    Присоединение пользователя к комнате.
    """
    serializer_class = UserInputSerializer
    queryset = Room.objects.all()

    def post(self, request, *args, **kwargs):
        room = self.get_object()

        if not room.current_meeting:
            raise ValidationError({"error": "In room no active meeting"})

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        nickname, role = serializer.validated_data["nickname"], serializer.validated_data["role"]
        cookie = self.request.COOKIES.get("user")
        token = cookie_decrypt(cookie) if cookie else str(uuid.uuid4())

        response = Response(serializer.data, status=status.HTTP_201_CREATED if cookie is None else status.HTTP_200_OK)
        if cookie is None:
            response.set_cookie("user", value=cookie_encrypt(token), max_age=432000)

        if check_token_in_cache(token):
            raise ValidationError({"error": "User exists"})

        save_new_client_to_cache(token, nickname, role)

        room.participants.append({token: role})
        room.current_meeting.votes[token] = None
        room.save(update_fields=["participants", "current_meeting"])

        send_to_room_group(
            room.id,
            {
                "type": "user_joined",
                "user": nickname,
                "role": role
            }
        )

        return response


class CurrentUserView(RetrieveAPIView):
    """
    Получение информации о текущем пользователе.
    """
    serializer_class = UserInputSerializer

    def get_object(self):
        cookie = str(self.request.COOKIES.get("user") or ValidationError("User cookie is empty"))
        token = cookie_decrypt(cookie)
        if token is None:
            raise ValidationError("User cookie is not valid")
        user_data = get_client_data_by_token(token)
        if not user_data:
            raise Http404("User not found")
        return user_data
