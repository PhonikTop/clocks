import uuid

from api.api_utils import APIResponseHandler
from django.shortcuts import get_object_or_404
from meetings.models import Meeting
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rooms.models import Room

from .redis_client import (
    check_token_in_db,
    save_new_client_to_redis,
)

response = APIResponseHandler()


class JoinRoomView(APIView):
    """
    Присоединение пользователя к комнате.
    """

    def post(self, request: Request) -> Response:
        nickname, room_id, role = map(request.data.get, ["nickname", "room_id", "role"])
        cookie, token = request.COOKIES.get("user"), str(uuid.uuid4())

        if not all([nickname, room_id, role]):
            return response.error_response(msg="Missing parameters", data=None,
                                           response_status=status.HTTP_400_BAD_REQUEST)

        if check_token_in_db(token):
            return response.error_response(msg="User exists", data=None,
                                           response_status=status.HTTP_400_BAD_REQUEST)

        save_new_client_to_redis(token, cookie, nickname, role)

        room: Room = get_object_or_404(Room, id=room_id)
        room.users.append({token: role})

        meeting: Meeting = room.current_meeting or Meeting.objects.create(room=room, task_name="Введите название таска")
        room.current_meeting = meeting

        room.save()
        meeting.votes[token] = None
        meeting.save()

        return response.success_response(msg="User joined", data={"user": nickname, "Meeting": meeting.id},
                                         response_status=status.HTTP_200_OK)


class CurrentUserView(APIView):
    """
    Получение информации о текущем пользователе.
    """

    def get(self, request: Request) -> Response:
        from .redis_client import get_client_data_by_cookie
        cookie = request.COOKIES.get("user")

        token, nickname, role = get_client_data_by_cookie(cookie)

        if not token or not nickname or not role:
            return response.error_response(msg="User not found", data=None, response_status=status.HTTP_404_NOT_FOUND)

        return response.success_response(msg="User info", data={"token": token, "nickname": nickname, "role": role},
                                         response_status=status.HTTP_200_OK)


class UserNicknameView(APIView):
    """
    Получение информации о текущем пользователе.
    """

    def get(self, request: Request) -> Response:
        from .redis_client import get_client_nickname
        token = request.data.get("token")
        nickname = get_client_nickname(token)

        if not nickname:
            return response.error_response(msg="User not found", data=None, response_status=status.HTTP_404_NOT_FOUND)

        return response.success_response(msg="User nickname", data={"nickname": nickname},
                                         response_status=status.HTTP_200_OK)
