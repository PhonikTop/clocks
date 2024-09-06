from api.api_utils import APIResponseHandler
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import (
    CreateAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    get_object_or_404,
)
from rest_framework.request import Request
from rest_framework.response import Response
from rooms.models import Room

from .models import Meeting
from .serializers import MeetingSerializer

response = APIResponseHandler()


class StartMeetingView(CreateAPIView):
    """
    Создание новой сессии для голосования в комнате.
    """
    serializer_class = MeetingSerializer

    def perform_create(self, serializer):
        room_id = self.request.data.get("room")
        task_name = self.request.data.get("task_name")

        room = get_object_or_404(Room, id=room_id)

        if room.current_meeting is not None:
            raise ValidationError({"error": "Room session already exists."})

        meeting = serializer.save(room=room, task_name=task_name)
        room.current_meeting = meeting
        room.save()
        return meeting

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({
            "msg": "Meeting started",
            "data": response.data
        }, status=status.HTTP_201_CREATED)


class GetMeetingView(RetrieveAPIView):
    """
    Получение информации о конкретной сессии.
    """
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    lookup_field = "id"

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        meeting = self.get_object()
        serializer = self.get_serializer(meeting,
                                         fields=["id", "room", "task_name", "votes", "average_score", "active"])
        return response.success_response(msg="Meeting info", data=serializer.data, response_status=status.HTTP_200_OK)


class EndMeetingView(UpdateAPIView):
    """
    Завершение текущего раунда голосования.
    """
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    lookup_field = "id"

    def update(self, request: Request, *args, **kwargs) -> Response:
        meeting = self.get_object()

        if not meeting.active:
            return response.error_response(msg="Meeting already completed", data=None,
                                           response_status=status.HTTP_400_BAD_REQUEST)
        meeting.active = False
        meeting.save()

        room = meeting.room
        room.current_meeting = None
        room.save()

        return response.success_response(msg="Meeting ended", data=None, response_status=status.HTTP_200_OK)


class RestartMeetingView(UpdateAPIView):
    """
    Перезапуск текущего раунда голосования.
    """
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    lookup_field = "id"

    def update(self, request: Request, *args, **kwargs) -> Response:
        meeting = self.get_object()
        room = meeting.room

        meeting.reset_to_default()

        if room.current_meeting is None:
            room.current_meeting = meeting
            room.save()

        return response.success_response(msg="Meeting Restarted", data=None, response_status=status.HTTP_200_OK)


class UpdateMeetingTaskView(UpdateAPIView):
    """
    Установка задачи для текущей сессии.
    """
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    lookup_field = "id"

    def update(self, request: Request, *args, **kwargs) -> Response:
        task_name = request.data.get("task_name")
        meeting = self.get_object()

        serializer = self.get_serializer(meeting, data={"task_name": task_name}, partial=True)
        if not serializer.is_valid():
            return response.error_response(msg="Error", data=serializer.errors,
                                           response_status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return response.success_response(msg="Task updated", data={"task_name": task_name},
                                         response_status=status.HTTP_200_OK)


class GetMeetingResultsView(RetrieveAPIView):
    """
    Получение результатов конкретной сессии.
    """
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    lookup_field = "id"

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        meeting = self.get_object()

        if meeting.votes:
            meeting.average_score = round(sum(int(value) for value in meeting.votes.values()) / len(meeting.votes))
        else:
            meeting.average_score = 0
        meeting.save()

        serializer = self.get_serializer(meeting, fields=["task_name", "votes", "average_score"])
        return response.success_response(msg="Meeting Results", data=serializer.data,
                                         response_status=status.HTTP_200_OK)
