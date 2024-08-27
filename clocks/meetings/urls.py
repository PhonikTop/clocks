import views
from django.urls import path

urlpatterns = [
    path("session", views.start_session, name="start_session"),
    path("session/<int:session_id>", views.get_session, name="get_session"),
    path("session/<int:session_id>/vote", views.vote, name="vote"),
    path("session/<int:session_id>/end", views.end_session, name="end_session"),
    path("session/<int:session_id>/task", views.update_session_task, name="update_session_task"),
    path("session/<int:session_id>/results", views.get_session_results, name="get_session_results"),
]
