from api.api_utils import APIResponseHandler
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rooms.models import Room

from .models import Meeting
from .serializers import MeetingSerializer

response = APIResponseHandler()


class StartMeetingView(APIView):
    """
    Создание новой сессии для голосования в комнате.
    """

    def post(self, request: Request) -> Response:
        room_id = request.data.get("room_id")
        task_name = request.data.get("task_name")

        if not room_id or not task_name:
            return response.error_response(msg="Missing parameters", data=None,
                                           response_status=status.HTTP_400_BAD_REQUEST)

        room = get_object_or_404(Room, id=room_id)

        if room.current_meeting is None:
            meeting = Meeting.objects.create(room=room, task_name=task_name)
            room.current_meeting = meeting
            room.save()

            serializer = MeetingSerializer(meeting, fields=["id", "room"])
            return response.success_response(msg="Meeting started", data=serializer.data,
                                             response_status=status.HTTP_201_CREATED)
        else:
            return response.error_response(msg="Room session exists", data=None,
                                           response_status=status.HTTP_400_BAD_REQUEST)


class GetMeetingView(APIView):
    """
    Получение информации о конкретной сессии.
    """

    def get(self, request: Request, meeting_id: int) -> Response:
        meeting = get_object_or_404(Meeting, id=meeting_id)
        serializer = MeetingSerializer(meeting, many=True,
                                       fields=["id", "room", "task_name", "votes", "average_score", "active"])
        return response.success_response(msg="Meeting info", data=serializer.data,
                                         response_status=status.HTTP_200_OK)


class VoteView(APIView):
    """
    Отправка голоса участника в текущей сессии.
    """

    def post(self, request: Request, meeting_id: int) -> Response:
        meeting = get_object_or_404(Meeting, id=meeting_id)
        user_name = request.data.get("user")
        user_vote = request.data.get("vote")

        if not user_name or user_vote is None:
            return response.error_response(msg="Missing parameters", data=None,
                                           response_status=status.HTTP_400_BAD_REQUEST)

        room: Room = get_object_or_404(Room, current_meeting_id=meeting_id)
        if not any(user_name in d for d in room.users):
            return response.error_response(msg="Participant doesn't exists", data=None,
                                           response_status=status.HTTP_400_BAD_REQUEST)

        meeting.votes[user_name] = user_vote
        meeting.save()

        return response.success_response(msg="Vote recorded", data=None,
                                         response_status=status.HTTP_200_OK)


class EndMeetingView(APIView):
    """
    Завершение текущего раунда голосования.
    """

    def post(self, request: Request, meeting_id: int) -> Response:
        meeting = get_object_or_404(Meeting, id=meeting_id)

        if not meeting.active:
            return response.error_response(msg="Meeting already completed", data=None,
                                           response_status=status.HTTP_400_BAD_REQUEST)
        meeting.active = False

        if meeting.votes:
            meeting.average_score = round(
                sum(int(value) for value in meeting.votes.values()) / len(meeting.votes)
            )
        else:
            meeting.average_score = 0
        meeting.save()

        return response.success_response(msg="Meeting ended", data={"average_score": meeting.average_score},
                                         response_status=status.HTTP_200_OK)


class UpdateMeetingTaskView(APIView):
    """
    Установка задачи для текущей сессии.
    """

    def post(self, request: Request, meeting_id: int) -> Response:
        meeting = get_object_or_404(Meeting, id=meeting_id)
        task_name = request.data.get("task_name")

        if not task_name:
            return response.error_response(msg="Task name is required", data=None,
                                           response_status=status.HTTP_400_BAD_REQUEST)

        meeting.task_name = task_name
        meeting.save()

        serializer = MeetingSerializer(data=request.data, fields=["task_name"])

        if serializer.is_valid():
            return response.success_response(msg="Task updated", data={"task_name": task_name},
                                             response_status=status.HTTP_200_OK)
        else:
            return response.error_response(msg="Error", data=serializer.errors,
                                           response_status=status.HTTP_400_BAD_REQUEST)


class GetMeetingResultsView(APIView):
    """
    Получение результатов конкретной сессии.
    """

    def get(self, request: Request, meeting_id: int) -> Response:
        meeting = get_object_or_404(Meeting, id=meeting_id)

        serializer = MeetingSerializer(meeting, fields=["task_name", "votes", "average_score"])
        return response.success_response(msg="Meeting Results", data=serializer.data,
                                         response_status=status.HTTP_200_OK)
