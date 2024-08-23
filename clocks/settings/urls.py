"""
URL configuration for settings project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# urls.py
from django.urls import path
from watchy import views

urlpatterns = [
    path("api/v1/user/join-room", views.join_room, name="join_room"),
    path("api/v1/user/current", views.get_current_user, name="get_current_user"),
    path("api/v1/rooms", views.get_rooms, name="get_rooms"),
    path("api/v1/room", views.create_room, name="create_room"),
    path("api/v1/room/get/<int:room_id>", views.get_room, name="get_room"),
    path("api/v1/room/del/<int:room_id>", views.delete_room, name="delete_room"),
    path("api/v1/room/<int:room_id>/participants", views.get_room_participants, name="get_room_participants"),
    path("api/v1/session", views.start_session, name="start_session"),
    path("api/v1/session/<int:session_id>", views.get_session, name="get_session"),
    path("api/v1/session/<int:session_id>/vote", views.vote, name="vote"),
    path("api/v1/session/<int:session_id>/end", views.end_session, name="end_session"),
    path("api/v1/session/<int:session_id>/task", views.update_session_task, name="update_session_task"),
    path("api/v1/room/<int:room_id>/history", views.get_room_history, name="get_room_history"),
    path("api/v1/session/<int:session_id>/results", views.get_session_results, name="get_session_results"),
]
