import uuid

from api.api_utils import Cookies_utils, send_to_room_group
from django.http import Http404
from django.shortcuts import get_object_or_404
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

cookie_utils = Cookies_utils()


class JoinRoomView(GenericAPIView):
    """
    Присоединение пользователя к комнате.
    """
    serializer_class = UserInputSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        nickname, role = serializer.validated_data["nickname"], serializer.validated_data["role"]
        cookie = self.request.COOKIES.get("user")
        token = cookie_utils.cookie_decrypt(cookie) if cookie else str(uuid.uuid4())

        if cookie is None:
            response = Response(serializer.data, status=status.HTTP_201_CREATED)
            response.set_cookie("user", value=cookie_utils.cookie_encrypt(token), max_age=432000)
        else:
            response = Response(serializer.data, status=status.HTTP_200_OK)

        if check_token_in_cache(token):
            raise ValidationError({"error": "User exists"})

        room = get_object_or_404(Room, id=self.request.data.get("room_id"))
        if room.current_meeting is None:
            raise ValidationError({"error": "In room no active meeting"})

        save_new_client_to_cache(token, nickname, role)

        room.participants.append({token: role})
        room.current_meeting.votes[token] = None
        room.save()

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
        token = cookie_utils.cookie_decrypt(str(self.request.COOKIES.get("user")))
        if token is None:
            raise ValidationError("User cookie not valid")
        user_data = get_client_data_by_token(token)
        if not all(user_data.values()):
            raise Http404("User not found")
        return user_data
