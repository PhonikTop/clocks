import uuid

from api.api_utils import APIResponseHandler
from django.shortcuts import get_object_or_404
from meetings.models import Meeting
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rooms.models import Room

from .redis_client import check_nickname_in_db, save_new_client_to_redis

response = APIResponseHandler()


class JoinRoomView(APIView):
    """
    Присоединение пользователя к комнате.
    """

    def post(self, request: Request) -> Response:
        nickname: str = request.data.get("nickname")
        room_id: int = request.data.get("room_id")
        role: str = request.data.get("role")
        token: str = str(uuid.uuid4())

        if not all([nickname, room_id, role]):
            return response.error_response(msg="Missing parameters", data=None,
                                           response_status=status.HTTP_400_BAD_REQUEST)

        if role not in ["observer", "participant"]:
            return response.error_response(msg="Invalid role", data=None,
                                           response_status=status.HTTP_400_BAD_REQUEST)

        if not check_nickname_in_db(token):
            cookie: str = request.COOKIES["user"]
            save_new_client_to_redis(token, cookie, nickname, role)

            room: Room = get_object_or_404(Room, id=room_id)
            room.users.append({token: role})
            room.save()

            meeting: Meeting = room.current_meeting
            if meeting is None:
                meeting = Meeting.objects.create(room_id=room, task_name="Введите название таска")
                room.current_meeting = meeting
                room.save()
            print(token)
            meeting.votes[token] = None
            meeting.save()

            return response.success_response(msg="User joined", data={"user": nickname, "Meeting": meeting.id},
                                             response_status=status.HTTP_200_OK)
        else:
            return response.error_response(msg="User exists", data=None,
                                           response_status=status.HTTP_400_BAD_REQUEST)


class CurrentUserView(APIView):
    """
    Получение информации о текущем пользователе.
    """

    def get(self, request: Request) -> Response:
        return response.success_response(msg="Not implemented", data=None,
                                         response_status=status.HTTP_201_CREATED)
