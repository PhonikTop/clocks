from datetime import datetime, timedelta, timezone
from unittest.mock import call, patch

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from rooms.models import Room
from rooms.services.room_cache_service import RoomCacheService


@pytest.mark.django_db
def test_create_room_admin(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)

    url = reverse("room_create")
    resp = api_client.post(url, {"name": "Room A"})
    assert resp.status_code == 201
    assert Room.objects.filter(name="Room A").exists()

@pytest.mark.django_db
def test_create_room_non_admin(api_client):
    user = User.objects.create_user(username="user1", password="password")
    api_client.force_authenticate(user=user)

    url = reverse("room_create")
    resp = api_client.post(url, {"name": "Room B"})
    assert resp.status_code == 403

def test_create_room_empty_name(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    resp = api_client.post(reverse("room_create"), {"name": ""})
    assert resp.status_code == 400

@pytest.mark.django_db
def test_list_rooms(api_client):
    Room.objects.create(name="Room1", active=True)
    Room.objects.create(name="Room2", active=False)

    url = reverse("room_list")
    resp = api_client.get(url)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "Room1"

@pytest.mark.django_db
def test_list_rooms_includes_active_meeting_id(api_client):
    Room.objects.create(name="RoomWithMeeting", active=True)
    Room.objects.create(name="RoomWithoutMeeting", active=True)

    url = reverse("room_list")
    resp = api_client.get(url)
    assert resp.status_code == 200
    data = resp.json()

    for item in data:
        assert "active_meeting_id" in item
        assert item["active_meeting_id"] is None or isinstance(item["active_meeting_id"], int)

@pytest.mark.django_db
def test_room_detail_get(api_client, room):
    url = reverse("room_detail", args=[room.id])
    resp = api_client.get(url)
    assert resp.status_code == 200
    assert resp.json()["name"] == room.name

@pytest.mark.django_db
def test_room_detail_not_found(api_client):
    url = reverse("room_detail", args=[9999])
    resp = api_client.get(url)
    assert resp.status_code == 404

@pytest.mark.django_db
def test_room_detail_delete_non_admin(api_client, room):
    url = reverse("room_detail", args=[room.id])
    resp = api_client.delete(url)
    assert resp.status_code == 401

@pytest.mark.django_db
def test_room_detail_delete_admin(api_client, admin_user, room):
    api_client.force_authenticate(user=admin_user)

    url = reverse("room_detail", args=[room.id])
    resp = api_client.delete(url)
    assert resp.status_code == 204
    assert not Room.objects.filter(id=room.id).exists()

@pytest.mark.django_db
def test_room_participants(api_client, room):
    url = reverse("room_participants", args=[room.id])

    with patch.object(RoomCacheService, "get_room_users", return_value={"user1": {"role": "voter", "nickname": "User1"}}):
        resp = api_client.get(url)
        assert resp.status_code == 200
        assert "participants" in resp.json()

@pytest.mark.django_db
def test_room_participants_none_returns_404(api_client, room):
    url = reverse("room_participants", args=[room.id])

    with patch.object(RoomCacheService, "get_room_users", return_value=None):
        resp = api_client.get(url)
        assert resp.status_code == 404
        assert "detail" in resp.json()

@pytest.mark.django_db
def test_room_timer_set(jwt_token, room, api_client):
    minutes = 5
    fixed_now = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    expected_timestamp = float((fixed_now + timedelta(minutes=minutes)).timestamp())

    with (patch("rooms.views.UserSessionService") as mock_user_session_cls,
         patch("rooms.views.JWTService") as mock_jwt_cls,
         patch("rooms.views.RoomMessageService") as mock_rms,
         patch("rooms.views.DjangoChannelMessageSender") as mock_sender_cls,
         patch("rooms.views.RoomCacheService") as mock_rcs,
         patch("rooms.views.datetime") as mock_datetime):

        mock_datetime.now.side_effect = lambda tz=None: fixed_now

        url = reverse("set_room_timer", args=[room.id])
        payload = {"minutes": minutes}

        resp1 = api_client.post(url, data=payload, format="json")
        assert resp1.status_code == 401

        api_client.credentials(HTTP_AUTHORIZATION="Token abc")
        resp2 = api_client.post(url, data=payload, format="json")
        assert resp2.status_code == 401

        user_uuid = "065e8922-5961-4584-8271-39eaeacbe677"

        mock_user_session_cls.return_value.get_user_uuid.return_value = user_uuid

        mock_rcs.return_value.get_user.return_value = None
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {jwt_token}")
        resp3 = api_client.post(url, data=payload, format="json")
        assert resp3.status_code == 401

        mock_rcs.return_value.get_user.return_value = {}
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {jwt_token}")
        resp = api_client.post(url, data=payload, format="json")

        mock_rms.assert_called_once_with(room.id, mock_sender_cls.return_value, mock_rcs.return_value)
        mock_rms.return_value.notify_room_timer_started.assert_called_once_with(expected_timestamp, user_uuid)

        assert mock_rcs.call_count == 2
        mock_rcs.return_value.start_room_timer.assert_called_once_with(expected_timestamp)
        mock_rcs.return_value.get_user.assert_has_calls([call(user_uuid),call(user_uuid)])

        assert resp.status_code == 200

@pytest.mark.django_db
def test_room_timer_set_invalid_minutes(api_client, room, jwt_token):
    with (patch("rooms.views.UserSessionService") as mock_user_session_cls, \
         patch("rooms.views.JWTService") as mock_jwt_cls, \
         patch("rooms.views.RoomMessageService") as mock_rms, \
         patch("rooms.views.DjangoChannelMessageSender"), \
         patch("rooms.views.RoomCacheService") as mock_rcs):

        payload = {"minutes": "invalid minutes"}
        url = reverse("set_room_timer", args=[room.id])

        resp = api_client.post(
            url, data=payload, format="json", HTTP_AUTHORIZATION=f"Bearer {jwt_token}"
        )

        assert resp.status_code == 400

@pytest.mark.django_db
def test_room_timer_get(api_client, room):
    with (patch("rooms.views.RoomCacheService") as mock_rcs):
        new_timestamp_str = int(
            (datetime.now(timezone.utc) + timedelta(minutes=5)).timestamp()
        )

        mock_rcs.return_value.get_room_timer.return_value = new_timestamp_str

        url = reverse("get_room_timer", args=[room.id])
        resp = api_client.get(url)

        mock_rcs.assert_called_once()
        mock_rcs.return_value.get_room_timer.assert_called_once()

        assert resp.status_code == 200
        body = resp.json()
        assert body["timer_end_time"] == new_timestamp_str

@pytest.mark.django_db
def test_room_timer_reset(api_client, room, jwt_token):
    with (patch("rooms.views.UserSessionService") as mock_user_session_cls, \
         patch("rooms.views.JWTService") as mock_jwt_cls, \
         patch("rooms.views.RoomMessageService") as mock_rms, \
         patch("rooms.views.DjangoChannelMessageSender") as mock_sender_cls, \
         patch("rooms.views.RoomCacheService") as mock_rcs):

        url = reverse("reset_room_timer", args=[room.id])

        resp1 = api_client.delete(url)
        assert resp1.status_code == 401

        api_client.credentials(HTTP_AUTHORIZATION="Token abc")
        resp2 = api_client.delete(url)
        assert resp2.status_code == 401

        user_uuid = "065e8922-5961-4584-8271-39eaeacbe677"

        mock_user_session_cls.return_value.get_user_uuid.return_value = user_uuid

        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {jwt_token}")
        mock_rcs.return_value.get_user.return_value = None
        resp3 = api_client.delete(url)
        assert resp3.status_code == 401

        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {jwt_token}")
        mock_rcs.return_value.get_user.return_value = {}
        resp = api_client.delete(url)

        mock_rms.assert_called_once_with(room.id, mock_sender_cls.return_value, mock_rcs.return_value)
        mock_rms.return_value.notify_room_timer_reset.assert_called_once_with(user_uuid)

        assert mock_rcs.call_count == 2
        mock_rcs.return_value.reset_room_timer.assert_called_once_with()
        mock_rcs.return_value.get_user.assert_has_calls([call(user_uuid),call(user_uuid)])

        assert resp.status_code == 200
