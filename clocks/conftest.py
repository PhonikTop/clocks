from uuid import uuid4

import pytest
from api.services.jwt_service import JWTService
from channels.routing import URLRouter
from django.contrib.auth import get_user_model
from django.urls import re_path
from rest_framework.test import APIClient
from ws.consumers import RoomConsumer

User = get_user_model()

# ------------------------
# DRF APIClient
# ------------------------
@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def jwt_token():
    return JWTService().generate_token(str(uuid4))

@pytest.fixture
def user(db):
    return User.objects.create_user(username="user1", password="pass")

@pytest.fixture
def room(db):
    from rooms.models import Room

    return Room.objects.create(name="Test Room")


@pytest.fixture
def meeting(db, room):
    from meetings.models import Meeting

    return Meeting.objects.create(room=room, task_name="Initial Task")

@pytest.fixture
def finished_meeting(db, room):
    from meetings.models import Meeting

    return Meeting.objects.create(room=room, task_name="Initial Task", average_score=4)

@pytest.fixture
def room_url_router():
    application = URLRouter(
        [
            re_path(r"^ws/room/(?P<id>\d+)/$", RoomConsumer.as_asgi()),
        ]
    )
    return application

