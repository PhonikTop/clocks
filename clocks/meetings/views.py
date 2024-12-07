from rest_framework.generics import (
    CreateAPIView,
    RetrieveAPIView,
    UpdateAPIView,
)
from rest_framework.response import Response

from .logic import end_meeting, meeting_results
from .models import Meeting
from .serializers import (
    MeetingCreateSerializer,
    MeetingGetSerializer,
    MeetingRemoveSerializer,
    MeetingResultsSerializer,
    MeetingUpdateSerializer,
)


class StartMeetingView(CreateAPIView):
    serializer_class = MeetingCreateSerializer

    def perform_create(self, serializer):
        serializer.save(room=serializer.validated_data["room"],
                        task_name=self.request.data.get("task_name"))


class GetMeetingView(RetrieveAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingGetSerializer


class EndMeetingView(UpdateAPIView):
    queryset = Meeting.objects.select_related("room").filter(active=True)
    serializer_class = MeetingRemoveSerializer

    def update(self, request, *args, **kwargs):
        meeting = self.get_object()
        serializer = self.get_serializer(meeting, data=request.data, partial=kwargs.pop("partial", False))
        serializer.is_valid(raise_exception=True)

        end_meeting(meeting)
        return Response(serializer.data)


class RestartMeetingView(UpdateAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingRemoveSerializer

    def update(self, request, *args, **kwargs):
        meeting = self.get_object()
        serializer = self.get_serializer(meeting, data=request.data, partial=kwargs.pop("partial", False))
        serializer.is_valid(raise_exception=True)

        meeting.reset_to_default()

        return Response(serializer.data)


class UpdateMeetingTaskView(UpdateAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingUpdateSerializer


class MeetingResultsView(UpdateAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingResultsSerializer

    def update(self, request, *args, **kwargs):
        meeting = self.get_object()
        serializer = self.get_serializer(meeting, data=request.data, partial=kwargs.pop("partial", False))
        serializer.is_valid(raise_exception=True)

        meeting_results(meeting)
        meeting.save()

        return Response(serializer.data)
