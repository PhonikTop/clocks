from django.urls import path

from .views import (
    EndMeetingView,
    GetMeetingResultsView,
    GetMeetingView,
    RestartMeetingView,
    StartMeetingView,
    UpdateMeetingTaskView,
)

urlpatterns = [
    path("", StartMeetingView.as_view(), name="start_meeting"),
    path("<int:pk>", GetMeetingView.as_view(), name="get_meeting"),
    path("<int:pk>/end", EndMeetingView.as_view(), name="end_meeting"),
    path("<int:pk>/restart", RestartMeetingView.as_view(), name="restart_meeting"),
    path("<int:pk>/task", UpdateMeetingTaskView.as_view(), name="update_meeting_task"),
    path("<int:pk>/results", GetMeetingResultsView.as_view(), name="get_meeting_results"),
]
