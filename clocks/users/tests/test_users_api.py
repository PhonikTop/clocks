from unittest.mock import ANY, patch

import pytest
from django.urls import reverse

from users.enums import UserRole


@pytest.mark.django_db
def test_join_room_success(api_client, room, jwt_token):
    url = reverse("join_room", kwargs={"pk": room.id})

    with (
        patch("users.views.UserSessionService") as mock_user_session,
        patch("users.views.RoomMessageService") as mock_room_msg,
        patch("users.views.DjangoChannelMessageSender"),
        patch("users.views.RoomCacheService")
    ):
        token = jwt_token
        mock_user_session.return_value.create_user_session.return_value = token

        data = {"nickname": "Bob", "role": "voter"}
        response = api_client.post(url, data, format="json")

        assert response.status_code == 200
        assert response.data == {"token": token}
        mock_room_msg.return_value.notify_user_joined.assert_called_once()
        mock_user_session.return_value.create_user_session.assert_called_once_with(ANY, UserRole.VOTER, "Bob")


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
def test_user_info_valid_token_returns_session_data(api_client, room, jwt_token):
    url = reverse("user_info", args=[room.id])

    with (
        patch("users.views.UserSessionService") as mock_user_session,
        patch("users.views.JWTService"),
        patch("users.views.RoomCacheService"),
    ):
        mock_user_session.return_value.get_user_session_data.return_value = {"user_uuid": "u1", "nickname": "n1"}

        response = api_client.get(url, HTTP_AUTHORIZATION=f"Bearer {jwt_token}")

        assert response.status_code == 200
        assert response.data == {"user_uuid": "u1", "nickname": "n1"}
        mock_user_session.return_value.get_user_session_data.assert_called_once_with(jwt_token)


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
def test_user_kick_success_calls_services(api_client, room, jwt_token):
    url = reverse("user_kick", args=[room.id])

    with (
        patch("users.views.UserSessionService") as mock_user_session,
        patch("users.views.JWTService"),
        patch("users.views.RoomCacheService") as mock_room_cache,
        patch("users.views.RoomMessageService") as mock_room_msg,
        patch("users.views.DjangoChannelMessageSender")
    ):

        mock_user_session.return_value.get_user_uuid.return_value = "kicker-uuid"

        response = api_client.post(
            url, {"user_uuid": "kicked-uuid"}, HTTP_AUTHORIZATION=f"Bearer {jwt_token}"
        )

        assert response.status_code == 200
        mock_user_session.return_value.get_user_uuid.assert_called_once_with(jwt_token)
        mock_room_msg.return_value.notify_user_kicked.assert_called_once_with("kicked-uuid", "kicker-uuid")
        mock_room_cache.return_value.remove_user_vote.assert_called_once_with("kicked-uuid")
        mock_room_cache.return_value.remove_user.assert_called_once_with("kicked-uuid")
