from api.api_utils import APIResponseHandler

# from django.contrib.auth.decorators import permission_required
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

        room = get_object_or_404(Room, id=room_id)
        serializer = MeetingSerializer(data=request.data, fields=["room", "task_name"])

        if not serializer.is_valid():
            return response.error_response(msg="Error", data=serializer.errors,
                                           response_status=status.HTTP_400_BAD_REQUEST)

        if room.current_meeting is not None:
            return response.error_response(msg="Room session exists", data=None,
                                           response_status=status.HTTP_400_BAD_REQUEST)

        meeting = Meeting.objects.create(room=room, task_name=task_name)
        serializer = MeetingSerializer(meeting, fields=["id", "room"])
        room.current_meeting = meeting
        room.save()

        return response.success_response(msg="Meeting started", data=serializer.data,
                                         response_status=status.HTTP_201_CREATED)


class GetMeetingView(APIView):
    """
    Получение информации о конкретной сессии.
    """

    def get(self, request: Request, meeting_id: int) -> Response:
        meeting = get_object_or_404(Meeting, id=meeting_id)
        serializer = MeetingSerializer(meeting,
                                       fields=["id", "room", "task_name", "votes", "average_score", "active"])
        return response.success_response(msg="Meeting info", data=serializer.data,
                                         response_status=status.HTTP_200_OK)


class EndMeetingView(APIView):
    """
    Завершение текущего раунда голосования.
    """

    def post(self, request: Request, meeting_id: int) -> Response:
        meeting = get_object_or_404(Meeting.objects.select_related("room"), id=meeting_id)

        if not meeting.active:
            return response.error_response(msg="Meeting already completed", data=None,
                                           response_status=status.HTTP_400_BAD_REQUEST)
        meeting.active = False
        meeting.save()

        room = meeting.room
        room.current_meeting = None
        room.save()

        return response.success_response(msg="Meeting ended", data=None,
                                         response_status=status.HTTP_200_OK)


class RestartMeetingView(APIView):
    """
    Перезапуск текущего раунда голосования.
    """

    def post(self, request: Request, meeting_id: int) -> Response:
        meeting = get_object_or_404(Meeting.objects.select_related("room"), id=meeting_id)

        Meeting.objects.filter(id=meeting_id).update(
            active=True,
            votes={},
            average_score=0
        )

        room = meeting.room

        if room.current_meeting is None:
            room.current_meeting = meeting_id
            room.save()

        return response.success_response(msg="Meeting Restarted", data=None,
                                         response_status=status.HTTP_200_OK)


class UpdateMeetingTaskView(APIView):
    """
    Установка задачи для текущей сессии.
    """

    def post(self, request: Request, meeting_id: int) -> Response:
        task_name = request.data.get("task_name")

        serializer = MeetingSerializer(data=request.data, fields=["task_name"])

        if not serializer.is_valid():
            return response.error_response(msg="Error", data=serializer.errors,
                                           response_status=status.HTTP_400_BAD_REQUEST)

        Meeting.objects.filter(id=meeting_id).update(task_name=task_name)

        return response.success_response(msg="Task updated", data={"task_name": task_name},
                                         response_status=status.HTTP_200_OK)


class GetMeetingResultsView(APIView):
    """
    Получение результатов конкретной сессии.
    """

    def get(self, request: Request, meeting_id: int) -> Response:
        meeting = get_object_or_404(Meeting, id=meeting_id)

        if meeting.votes:
            meeting.average_score = round(
                sum(int(value) for value in meeting.votes.values()) / len(meeting.votes)
            )
        else:
            meeting.average_score = 0
        meeting.save()

        serializer = MeetingSerializer(meeting, fields=["task_name", "votes", "average_score"])
        return response.success_response(msg="Meeting Results", data=serializer.data,
                                         response_status=status.HTTP_200_OK)
