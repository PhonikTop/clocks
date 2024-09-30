from rest_framework.exceptions import ValidationError
from rest_framework.generics import (
    CreateAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    get_object_or_404,
)

from clocks.meetings.models import Meeting
from clocks.meetings.serializers import (
    MeetingCreateSerializer,
    MeetingGetSerializer,
    MeetingRemoveSerializer,
    MeetingResultsSerializer,
    MeetingUpdateSerializer,
)
from clocks.rooms.models import Room


class StartMeetingView(CreateAPIView):
    serializer_class = MeetingCreateSerializer

    def perform_create(self, serializer):
        room = get_object_or_404(Room, id=self.request.data.get("room"))

        if room.current_meeting:
            raise ValidationError({"error": "Room session already exists."})

        meeting = serializer.save(room=room, task_name=self.request.data.get("task_name"))
        room.current_meeting = meeting
        room.save()


class GetMeetingView(RetrieveAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingGetSerializer


class EndMeetingView(UpdateAPIView):
    queryset = Meeting.objects.select_related("room").filter(active=True)
    serializer_class = MeetingRemoveSerializer

    def perform_update(self, request, *args, **kwargs):
        meeting = self.get_object()

        if not meeting.active:
            raise ValidationError({"error": "Meeting already completed."})

        meeting.end_meeting()


class RestartMeetingView(UpdateAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingRemoveSerializer

    def perform_update(self, request, *args, **kwargs):
        meeting = self.get_object()

        meeting.reset_to_default()
        if not meeting.room.current_meeting:
            meeting.room.current_meeting = meeting
            meeting.room.save()


class UpdateMeetingTaskView(UpdateAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingUpdateSerializer


class MeetingResultsView(UpdateAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingResultsSerializer

    def perform_update(self, request, *args, **kwargs):
        meeting = self.get_object()
        meeting.get_average_score()
        meeting.save()
