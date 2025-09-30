import json
from unittest.mock import ANY, MagicMock, patch

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_start_voting_creates_and_notifies(api_client, room):
    url = reverse("start_voting")
    payload = {"room": room.id, "task_name": "Разработка архитектуры"}

    with patch("votings.views.RoomMessageService") as MockRMS, patch(
        "votings.views.DjangoChannelMessageSender"
    ):
        MockRMS.return_value.notify_voting_started = MagicMock()

        resp = api_client.post(url, data=payload, format="json")

        assert resp.status_code == 201, resp.content
        data = resp.json()
        assert "id" in data
        assert data["room"] == room.id
        assert data["task_name"] == "Разработка архитектуры"

        MockRMS.assert_called_once()
        MockRMS.return_value.notify_voting_started.assert_called_once_with(data["id"])


@pytest.mark.django_db
def test_start_voting_validation_when_active_exists(api_client, room, voting):
    url = reverse("start_voting")
    payload = {"room": room.id, "task_name": "Еще одна задача"}

    resp = api_client.post(url, data=payload, format="json")

    assert resp.status_code == 400
    body = resp.json()
    assert "error" in body
    assert "Room voting already exists" in json.dumps(body)


@pytest.mark.django_db
def test_get_voting_returns_info(api_client, voting):
    url = reverse("get_voting", kwargs={"pk": voting.id})
    resp = api_client.get(url)

    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == voting.id
    assert body["task_name"] == voting.task_name
    assert body["room"] == voting.room.id


@pytest.mark.django_db
def test_end_voting_only_active_allowed_and_calls_end_voting(api_client, voting):
    url = reverse("end_voting", kwargs={"pk": voting.id})
    with patch("votings.views.end_voting") as mock_end:
        mock_end.return_value = None
        resp = api_client.put(url, data={}, format="json")
        assert resp.status_code == 200
        mock_end.assert_called_once()
        assert resp.json()["id"] == voting.id

    voting.active = False
    voting.save()

    resp2 = api_client.put(url, data={}, format="json")
    assert resp2.status_code == 404


@pytest.mark.django_db
def test_restart_voting_calls_services_and_resets_voting(api_client, voting):
    url = reverse("restart_voting", kwargs={"pk": voting.id})

    with patch("votings.views.DjangoChannelMessageSender"), patch(
        "votings.views.RoomMessageService"
    ) as MockRMS, patch("votings.views.RoomCacheService") as MockRoomCache, patch(
        "votings.views.RoomOnlineTracker"
    ) as MockTracker:
        MockRMS.return_value.notify_voting_restart = MagicMock()
        MockRoomCache.return_value.clear_votes = MagicMock()
        MockTracker.return_value.clean_room_offline_participants = MagicMock()

        resp = api_client.put(url, data={}, format="json")
        assert resp.status_code == 200
        MockRoomCache.assert_called_once_with(voting.room.id)
        MockRoomCache.return_value.clear_votes.assert_called_once()
        MockTracker.return_value.clean_room_offline_participants.assert_called_once_with(voting.room.id)
        MockRMS.return_value.notify_voting_restart.assert_called_once()

        voting.refresh_from_db()
        assert voting.active is True
        assert voting.votes == {}
        assert voting.average_score is None


@pytest.mark.django_db
def test_update_voting_task_requires_authorization_and_notifies(api_client, voting, jwt_token):
    url = reverse("update_voting_task", kwargs={"pk": voting.id})
    payload = {"task_name": "Новое имя задачи"}

    resp1 = api_client.put(url, data=payload, format="json")
    assert resp1.status_code == 401

    api_client.credentials(HTTP_AUTHORIZATION="Token abc")
    resp2 = api_client.put(url, data=payload, format="json")
    assert resp2.status_code == 401

    api_client.credentials()
    token = jwt_token
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    with patch("votings.views.JWTService") as MockJWT, patch(
        "votings.views.RoomCacheService"
    ) as MockRoomCache, patch("votings.views.UserSessionService") as MockUSS, patch(
        "votings.views.RoomMessageService"
    ) as MockRMS:

        MockJWT.return_value.decode.return_value = {
            "user_id": 123,
            "nickname": "TesterNick",
        }

        instance_uss = MockUSS.return_value
        instance_uss.get_user_session_data.return_value = {"user_uuid": 123, "nickname": "TesterNick"}

        MockRoomCache.return_value = MagicMock()

        MockRMS.return_value.notify_voting_task_name_changed = MagicMock()

        resp3 = api_client.put(url, data=payload, format="json")
        assert resp3.status_code == 200

        body = resp3.json()
        assert body["task_name"] == "Новое имя задачи"

        instance_uss.get_user_session_data.assert_called_once_with(token)

        MockRMS.assert_called_once_with(voting.room.id, ANY)
        MockRMS.return_value.notify_voting_task_name_changed.assert_called_once_with("Новое имя задачи", "TesterNick")


@pytest.mark.django_db
def test_voting_results_computes_and_returns_votes_and_average(api_client, voting):
    url = reverse("get_voting_results", kwargs={"pk": voting.id})

    def fake_voting_results(voting_obj):
        votes = {
            "ed445c68-f4a4-40ba-b316-9f528603481d": {"nickname": "User1", "vote": 4},
            "a9115cc2-5c7c-4e1a-b5bd-61ed99c7492c": {"nickname": "User2", "vote": 12},
        }
        voting_obj.votes = votes
        voting_obj.average_score = 8.0
        voting_obj.save()

    with patch("votings.views.voting_results", side_effect=fake_voting_results) as mock_results:
        resp = api_client.put(url, data={}, format="json")
        assert resp.status_code == 200
        body = resp.json()
        assert "votes" in body
        assert body["average_score"] == 8.0
        mock_results.assert_called_once()
