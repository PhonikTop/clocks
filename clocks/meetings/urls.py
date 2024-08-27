from django.urls import path

from .views import (
    EndSessionView,
    GetSessionResultsView,
    GetSessionView,
    StartSessionView,
    UpdateSessionTaskView,
    VoteView,
)

urlpatterns = [
    path("", StartSessionView.as_view(), name='start_session'),
    path("<int:session_id>", GetSessionView.as_view(), name="get_session"),
    path("<int:session_id>/vote", VoteView.as_view(), name="vote"),
    path("<int:session_id>/end", EndSessionView.as_view(), name="end_session"),
    path("<int:session_id>/task", UpdateSessionTaskView.as_view(), name="update_session_task"),
    path("<int:session_id>/results", GetSessionResultsView.as_view(), name="get_session_results"),
]
