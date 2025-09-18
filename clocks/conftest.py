import pytest
from rest_framework.test import APIClient


# ------------------------
# DRF APIClient
# ------------------------
@pytest.fixture
def api_client():
    return APIClient()

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
