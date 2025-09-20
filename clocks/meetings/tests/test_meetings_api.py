import json
from unittest.mock import ANY, MagicMock, patch

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_start_meeting_creates_and_notifies(api_client, room):
    url = reverse("start_meeting")
    payload = {"room": room.id, "task_name": "Разработка архитектуры"}

    with patch("meetings.views.RoomMessageService") as MockRMS, patch(
        "meetings.views.DjangoChannelMessageSender"
    ):
        MockRMS.return_value.notify_meeting_started = MagicMock()

        resp = api_client.post(url, data=payload, format="json")

        assert resp.status_code == 201, resp.content
        data = resp.json()
        assert "id" in data
        assert data["room"] == room.id
        assert data["task_name"] == "Разработка архитектуры"

        MockRMS.assert_called_once()
        MockRMS.return_value.notify_meeting_started.assert_called_once_with(data["id"])


@pytest.mark.django_db
def test_start_meeting_validation_when_active_exists(api_client, room, meeting):
    url = reverse("start_meeting")
    payload = {"room": room.id, "task_name": "Еще одна задача"}

    resp = api_client.post(url, data=payload, format="json")

    assert resp.status_code == 400
    body = resp.json()
    assert "error" in body
    assert "Room meeting already exists" in json.dumps(body)


@pytest.mark.django_db
def test_get_meeting_returns_info(api_client, meeting):
    url = reverse("get_meeting", kwargs={"pk": meeting.id})
    resp = api_client.get(url)

    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == meeting.id
    assert body["task_name"] == meeting.task_name
    assert body["room"] == meeting.room.id


@pytest.mark.django_db
def test_end_meeting_only_active_allowed_and_calls_end_meeting(api_client, meeting):
    url = reverse("end_meeting", kwargs={"pk": meeting.id})
    with patch("meetings.views.end_meeting") as mock_end:
        mock_end.return_value = None
        resp = api_client.put(url, data={}, format="json")
        assert resp.status_code == 200
        mock_end.assert_called_once()
        assert resp.json()["id"] == meeting.id

    meeting.active = False
    meeting.save()

    resp2 = api_client.put(url, data={}, format="json")
    assert resp2.status_code == 404


@pytest.mark.django_db
def test_restart_meeting_calls_services_and_resets_meeting(api_client, meeting):
    url = reverse("restart_meeting", kwargs={"pk": meeting.id})

    with patch("meetings.views.DjangoChannelMessageSender"), patch(
        "meetings.views.RoomMessageService"
    ) as MockRMS, patch("meetings.views.RoomCacheService") as MockRoomCache, patch(
        "meetings.views.RoomOnlineTracker"
    ) as MockTracker:
        MockRMS.return_value.notify_meeting_restart = MagicMock()
        MockRoomCache.return_value.clear_votes = MagicMock()
        MockTracker.return_value.clean_room_offline_participants = MagicMock()

        resp = api_client.put(url, data={}, format="json")
        assert resp.status_code == 200
        MockRoomCache.assert_called_once_with(meeting.room.id)
        MockRoomCache.return_value.clear_votes.assert_called_once()
        MockTracker.return_value.clean_room_offline_participants.assert_called_once_with(meeting.room.id)
        MockRMS.return_value.notify_meeting_restart.assert_called_once()

        meeting.refresh_from_db()
        assert meeting.active is True
        assert meeting.votes == {}
        assert meeting.average_score is None


@pytest.mark.django_db
def test_update_meeting_task_requires_authorization_and_notifies(api_client, meeting, jwt_token):
    url = reverse("update_meeting_task", kwargs={"pk": meeting.id})
    payload = {"task_name": "Новое имя задачи"}

    resp1 = api_client.put(url, data=payload, format="json")
    assert resp1.status_code == 401

    api_client.credentials(HTTP_AUTHORIZATION="Token abc")
    resp2 = api_client.put(url, data=payload, format="json")
    assert resp2.status_code == 401

    api_client.credentials()
    token = jwt_token
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    with patch("meetings.views.JWTService") as MockJWT, patch(
        "meetings.views.RoomCacheService"
    ) as MockRoomCache, patch("meetings.views.UserSessionService") as MockUSS, patch(
        "meetings.views.RoomMessageService"
    ) as MockRMS:

        MockJWT.return_value.decode.return_value = {
            "user_id": 123,
            "nickname": "TesterNick",
        }

        instance_uss = MockUSS.return_value
        instance_uss.get_user_session_data.return_value = {"nickname": "TesterNick"}

        MockRoomCache.return_value = MagicMock()

        MockRMS.return_value.notify_meeting_task_name_changed = MagicMock()

        resp3 = api_client.put(url, data=payload, format="json")
        assert resp3.status_code == 200

        body = resp3.json()
        assert body["task_name"] == "Новое имя задачи"

        instance_uss.get_user_session_data.assert_called_once_with(token)

        MockRMS.assert_called_once_with(meeting.room.id, ANY)
        MockRMS.return_value.notify_meeting_task_name_changed.assert_called_once_with("Новое имя задачи", "TesterNick")


@pytest.mark.django_db
def test_meeting_results_computes_and_returns_votes_and_average(api_client, meeting):
    url = reverse("get_meeting_results", kwargs={"pk": meeting.id})

    def fake_meeting_results(meeting_obj):
        votes = {
            "ed445c68-f4a4-40ba-b316-9f528603481d": {"nickname": "User1", "vote": 4},
            "a9115cc2-5c7c-4e1a-b5bd-61ed99c7492c": {"nickname": "User2", "vote": 12},
        }
        meeting_obj.votes = votes
        meeting_obj.average_score = 8.0
        meeting_obj.save()

    with patch("meetings.views.meeting_results", side_effect=fake_meeting_results) as mock_results:
        resp = api_client.put(url, data={}, format="json")
        assert resp.status_code == 200
        body = resp.json()
        assert "votes" in body
        assert body["average_score"] == 8.0
        mock_results.assert_called_once()

@pytest.mark.django_db
def test_timer_set(meeting, jwt_token, api_client):
    token = jwt_token

    with (patch("meetings.views.UserSessionService") as mock_user_session_cls, \
         patch("meetings.views.JWTService") as mock_jwt_cls, \
         patch("meetings.views.RoomMessageService") as mock_rms, \
         patch("meetings.views.DjangoChannelMessageSender"), \
         patch("meetings.views.RoomCacheService") as mock_rcs):

        url = reverse("meeting_timer")
        payload = {"token": token, "minutes": 5}

        resp1 = api_client.put(url, data=payload, format="json")
        assert resp1.status_code == 401

        api_client.credentials(HTTP_AUTHORIZATION="Token abc")
        resp2 = api_client.put(url, data=payload, format="json")
        assert resp2.status_code == 401

        resp = api_client.post(
            url, data=payload, format="json", HTTP_AUTHORIZATION=f"Bearer {jwt_token}"
        )

        mock_user_session_cls.get_user_session_data.return_value = {"user_uuid": "uu"}

        mock_rms.assert_called_once()
        mock_rms.return_value.notify_meeting_timer.assert_called_once_with(resp["time"])

        mock_rcs.assert_called_once()
        mock_rcs.return_value.start_meeting_timer.assert_called_once_with(resp["time"])

        assert resp.status_code == 200

@pytest.mark.django_db
def test_timer_set_invalid_minutes(api_client, jwt_token):

    with (patch("meetings.views.UserSessionService") as mock_user_session_cls, \
         patch("meetings.views.JWTService") as mock_jwt_cls, \
         patch("meetings.views.RoomMessageService") as mock_rms, \
         patch("meetings.views.DjangoChannelMessageSender"), \
         patch("meetings.views.RoomCacheService") as mock_rcs):

        url = reverse("meeting_timer")
        payload = {"minutes": "invalid minutes"}

        resp = api_client.post(
            url, data=payload, format="json", HTTP_AUTHORIZATION=f"Bearer {jwt_token}"
        )

        assert resp.status_code == 400
        body = resp.json()
        assert "error" in body
        assert "Invalid minutes format" in json.dumps(body)
