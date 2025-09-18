from unittest.mock import MagicMock

import pytest
from django.urls import reverse
from rest_framework.test import APIRequestFactory

from users.enums import UserRole
from users.views import JoinRoomView, UserInfoView, UserKickView


@pytest.mark.django_db
def test_join_room_success(room, jwt_token, monkeypatch):
    factory = APIRequestFactory()
    data = {"nickname": "Bob", "role": "voter"}
    request = factory.post("/", data, format="json")

    token = jwt_token

    mock_user_session = MagicMock()
    mock_user_session.create_user_session.return_value = token

    monkeypatch.setattr("users.views.UserSessionService", lambda jwt, cache: mock_user_session)

    mock_room_msg = MagicMock()
    monkeypatch.setattr("users.views.RoomMessageService", lambda room_id, sender, cache: mock_room_msg)

    monkeypatch.setattr("users.views.DjangoChannelMessageSender", lambda: MagicMock())
    monkeypatch.setattr("users.views.RoomCacheService", lambda room_id: MagicMock())

    view = JoinRoomView.as_view()
    response = view(request, pk=room.id)

    assert response.status_code == 200
    assert response.data == {"token": token}
    mock_room_msg.notify_user_joined.assert_called_once()

    assert mock_user_session.create_user_session.called
    call_args = mock_user_session.create_user_session.call_args[0]
    assert isinstance(call_args[0], str)
    assert call_args[1] == UserRole.VOTER
    assert call_args[2] == "Bob"


@pytest.mark.django_db
def test_join_room_invalid_role_returns_400(api_client, room):
    url = reverse("join_room", args=[room.id])

    data = {"nickname": "Alice", "role": "invalid_role"}
    response = api_client.post(url, data)

    assert response.status_code == 400


@pytest.mark.django_db
def test_user_info_missing_authorization_raises(api_client, room):
    url = reverse("user_info", args=[room.id])

    response = api_client.get(url)
    assert response.status_code == 401


@pytest.mark.django_db
def test_user_info_invalid_format_raises(api_client, room):
    url = reverse("user_info", args=[room.id])

    response = api_client.get(url, HTTP_AUTHORIZATION="Token some_token_here")

    assert "Неверный формат токена" in str(response.data["detail"])


@pytest.mark.django_db
def test_user_info_valid_token_returns_session_data(monkeypatch, room, jwt_token):
    token = jwt_token
    factory = APIRequestFactory()
    request = factory.get("/", HTTP_AUTHORIZATION=f"Bearer {token}")

    mock_user_session = MagicMock()
    mock_user_session.get_user_session_data.return_value = {"user_uuid": "u1", "nickname": "n1"}

    monkeypatch.setattr("users.views.UserSessionService", lambda jwt, cache: mock_user_session)
    monkeypatch.setattr("users.views.JWTService", lambda: MagicMock())
    monkeypatch.setattr("users.views.RoomCacheService", lambda rid: MagicMock())

    view = UserInfoView.as_view()
    response = view(request, pk=room.id)

    assert response.status_code == 200
    assert response.data == {"user_uuid": "u1", "nickname": "n1"}
    mock_user_session.get_user_session_data.assert_called_once_with(token)


@pytest.mark.django_db
def test_user_kick_missing_authorization_raises(api_client, room):
    url = reverse("user_kick", args=[room.id])

    response = api_client.post(url, {"user_uuid": "k1"})

    assert response.status_code == 401
    assert "Токен не предоставлен" in str(response.data["detail"])

@pytest.mark.django_db
def test_user_kick_invalid_format_raises(api_client, room):
    url = reverse("user_kick", args=[room.id])

    response = api_client.post(url, {"user_uuid": "k1"}, HTTP_AUTHORIZATION="Token bad")

    assert response.status_code == 401
    assert "Неверный формат токена" in str(response.data["detail"])


@pytest.mark.django_db
def test_user_kick_success_calls_services(monkeypatch, room):
    factory = APIRequestFactory()
    request = factory.post("/", {"user_uuid": "kicked-uuid"}, format="json", HTTP_AUTHORIZATION="Bearer kickertoken")

    mock_user_session = MagicMock()
    mock_user_session.get_user_uuid.return_value = "kicker-uuid"
    monkeypatch.setattr("users.views.UserSessionService", lambda jwt, cache: mock_user_session)
    monkeypatch.setattr("users.views.JWTService", lambda: MagicMock())

    mock_room_cache = MagicMock()
    monkeypatch.setattr("users.views.RoomCacheService", lambda arg: mock_room_cache)

    mock_room_msg = MagicMock()
    monkeypatch.setattr("users.views.RoomMessageService", lambda room_id, sender, cache: mock_room_msg)
    monkeypatch.setattr("users.views.DjangoChannelMessageSender", lambda: MagicMock())

    view = UserKickView.as_view()
    response = view(request, pk=room.id)

    assert response.status_code == 200
    mock_user_session.get_user_uuid.assert_called_once_with("kickertoken")
    mock_room_msg.notify_user_kicked.assert_called_once_with("kicked-uuid", "kicker-uuid")
    mock_room_cache.remove_user_vote.assert_called_once_with("kicked-uuid")
    mock_room_cache.remove_user.assert_called_once_with("kicked-uuid")
