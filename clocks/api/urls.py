from django.urls import include, path

# Import views from all api applications
from meetings import views as meetings

urlpatterns = [
    path("user/", include("users.urls")),
    path("room/", include("rooms.urls")),

    path("session", meetings.start_session, name="start_session"),
    path("session/<int:session_id>", meetings.get_session, name="get_session"),
    path("session/<int:session_id>/vote", meetings.vote, name="vote"),
    path("session/<int:session_id>/end", meetings.end_session, name="end_session"),
    path("session/<int:session_id>/task", meetings.update_session_task, name="update_session_task"),
    path("session/<int:session_id>/results", meetings.get_session_results, name="get_session_results"),
]
