from api.api_utils import APIResponseHandler
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import (
    CreateAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    get_object_or_404,
)
from rooms.models import Room

from .models import Meeting
from .serializers import MeetingSerializer

response = APIResponseHandler()


class StartMeetingView(CreateAPIView):
    serializer_class = MeetingSerializer

    def perform_create(self, serializer):
        room = get_object_or_404(Room, id=self.request.data.get("room"))

        if room.current_meeting:
            raise ValidationError({"error": "Room session already exists."})

        meeting = serializer.save(room=room, task_name=self.request.data.get("task_name"))
        room.current_meeting = meeting
        room.save()


class GetMeetingView(RetrieveAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    lookup_field = "id"

    def get_serializer(self, *args, **kwargs):
        kwargs["fields"] = ["id", "room", "task_name", "votes", "average_score", "active"]
        return super().get_serializer(*args, **kwargs)


class EndMeetingView(UpdateAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        meeting = self.get_object()

        if not meeting.active:
            raise ValidationError({"error": "Meeting already completed."})

        meeting.active = False
        meeting.room.current_meeting = None
        meeting.room.save()
        meeting.save()

        return response.success_response(msg="Meeting ended", response_status=status.HTTP_200_OK)


class RestartMeetingView(UpdateAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        meeting = self.get_object()

        meeting.reset_to_default()
        if not meeting.room.current_meeting:
            meeting.room.current_meeting = meeting
            meeting.room.save()

        return response.success_response(msg="Meeting Restarted", response_status=status.HTTP_200_OK)


class UpdateMeetingTaskView(UpdateAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data={"task_name": request.data.get("task_name")},
                                         partial=True)

        if not serializer.is_valid():
            return response.error_response(msg="Error", data=serializer.errors,
                                           response_status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return response.success_response(msg="Task updated", data={"task_name": request.data.get("task_name")},
                                         response_status=status.HTTP_200_OK)


class GetMeetingResultsView(RetrieveAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    lookup_field = "id"

    def retrieve(self, request, *args, **kwargs):
        meeting = self.get_object()
        meeting.average_score = round(
            sum(map(int, meeting.votes.values())) / len(meeting.votes)) if meeting.votes else 0
        meeting.save()

        serializer = self.get_serializer(meeting, fields=["task_name", "votes", "average_score"])
        return response.success_response(msg="Meeting Results", data=serializer.data,
                                         response_status=status.HTTP_200_OK)
