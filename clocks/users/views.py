from api.api_utils import APIResponseHandler
from django.shortcuts import get_object_or_404
from meetings.models import Meeting
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rooms.models import Room

from .redis_client import RedisClient

response = APIResponseHandler()
redis = RedisClient()


class JoinRoomView(APIView):
    """
    Присоединение пользователя к комнате.
    """

    def post(self, request: Request) -> Response:
        nickname, room_id, role = map(request.data.get, ["nickname", "room_id", "role"])
        cookie = request.COOKIES.get("user")

        if not all([nickname, room_id, role]):
            return response.error_response(msg="Missing parameters", data=None,
                                           response_status=status.HTTP_400_BAD_REQUEST)

        if redis.check_token_in_db(cookie):
            return response.error_response(msg="User exists", data=None,
                                           response_status=status.HTTP_400_BAD_REQUEST)

        redis.save_new_client_to_redis(cookie, nickname, role)

        room: Room = get_object_or_404(Room, id=room_id)
        room.users.append({cookie: role})

        meeting: Meeting = room.current_meeting or Meeting.objects.create(room=room, task_name="Введите название таска")
        room.current_meeting = meeting

        room.save()
        meeting.votes[cookie] = None
        meeting.save()

        return response.success_response(msg="User joined", data={"user": nickname, "Meeting": meeting.id},
                                         response_status=status.HTTP_200_OK)


class CurrentUserView(APIView):
    """
    Получение информации о текущем пользователе.
    """

    def get(self, request: Request) -> Response:
        cookie = request.COOKIES.get("user")

        nickname, role = redis.get_client_data_by_cookie(cookie).values()

        if not all([nickname, role]):
            return response.error_response(msg="User not found", data=None, response_status=status.HTTP_404_NOT_FOUND)

        return response.success_response(msg="User info", data={"token": cookie, "nickname": nickname, "role": role},
                                         response_status=status.HTTP_200_OK)
