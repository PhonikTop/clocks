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
from watchy.views import (
    join_room, get_current_user, get_rooms, create_room, get_room,
    delete_room, get_room_participants, start_session, get_session, vote,
    end_session, update_session_task, get_room_history, get_session_results
)

urlpatterns = [
    path('api/v1/user/join-room', join_room, name='join_room'),
    path('api/v1/user/current', get_current_user, name='get_current_user'),
    path('api/v1/rooms', get_rooms, name='get_rooms'),
    path('api/v1/room', create_room, name='create_room'),
    path('api/v1/room/get/<int:room_id>', get_room, name='get_room'),
    path('api/v1/room/del/<int:room_id>', delete_room, name='delete_room'),
    path('api/v1/room/<int:room_id>/participants', get_room_participants, name='get_room_participants'),
    path('api/v1/session', start_session, name='start_session'),
    path('api/v1/session/<int:session_id>', get_session, name='get_session'),
    path('api/v1/session/<int:session_id>/vote', vote, name='vote'),
    path('api/v1/session/<int:session_id>/end', end_session, name='end_session'),
    path('api/v1/session/<int:session_id>/task', update_session_task, name='update_session_task'),
    path('api/v1/room/<int:room_id>/history', get_room_history, name='get_room_history'),
    path('api/v1/session/<int:session_id>/results', get_session_results, name='get_session_results'),
]
