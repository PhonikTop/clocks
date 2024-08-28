from django.urls import path

from .views import (
    EndMeetingView,
    GetMeetingResultsView,
    GetMeetingView,
    StartMeetingView,
    UpdateMeetingTaskView,
    VoteView,
)

urlpatterns = [
    path("", StartMeetingView.as_view(), name="start_meeting"),
    path("<int:meeting_id>", GetMeetingView.as_view(), name="get_meeting"),
    path("<int:meeting_id>/vote", VoteView.as_view(), name="vote"),
    path("<int:meeting_id>/end", EndMeetingView.as_view(), name="end_meeting"),
    path("<int:meeting_id>/task", UpdateMeetingTaskView.as_view(), name="update_meeting_task"),
    path("<int:meeting_id>/results", GetMeetingResultsView.as_view(), name="get_meeting_results"),
]
