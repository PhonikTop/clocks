from unittest.mock import MagicMock, patch

import pytest

from ws.actions import ChangeVotingStatus, SubmitVoteAction


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_submit_vote_invalid_format():
    consumer = MagicMock()
    consumer.lookup_id = 1
    res = await SubmitVoteAction.execute(consumer, {"token": "t", "vote": "not-int"})
    assert res == {"error": "Invalid vote format"}

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_submit_vote_participant_not_found(voting):
    consumer = MagicMock()
    consumer.lookup_id = voting.room.id
    token = "tkn"
    with patch("ws.actions.RoomCacheService") as mock_room_cache_cls, \
         patch("ws.actions.UserSessionService") as mock_user_session_cls, \
         patch("ws.actions.JWTService") as mock_jwt_cls:

        mock_cache = mock_room_cache_cls.return_value
        mock_cache.get_users_by_role.return_value = ["other-user"]

        mock_user_session = mock_user_session_cls.return_value
        mock_user_session.get_user_session_data.return_value = {"user_uuid": "u1"}

        with patch.object(SubmitVoteAction, "get_object", return_value=voting):
            res = await SubmitVoteAction.execute(consumer, {"token": token, "vote": "5"})
            assert res == {"error": "Participant not found"}

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_submit_vote_success_not_finish(voting):
    consumer = MagicMock()
    consumer.lookup_id = voting.room.id
    token = "tkn"
    with patch("ws.actions.RoomCacheService") as mock_room_cache_cls, \
         patch("ws.actions.UserSessionService") as mock_user_session_cls, \
         patch("ws.actions.JWTService") as mock_jwt_cls, \
         patch("ws.actions.check_voting_finish") as mock_check_finish:

        mock_cache = mock_room_cache_cls.return_value
        mock_cache.get_users_by_role.return_value = ["uA", "uB"]
        mock_cache.set_vote.return_value = None

        mock_user_session = mock_user_session_cls.return_value
        mock_user_session.get_user_session_data.return_value = {"user_uuid": "uA"}

        mock_check_finish.return_value = False

        with patch.object(SubmitVoteAction, "get_object", return_value=voting):
            res = await SubmitVoteAction.execute(consumer, {"token": token, "vote": "3"})
            assert res == {"type": "user_voted", "user": "uA"}

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_submit_vote_finishes_voting_and_returns_results(voting):
    consumer = MagicMock()
    consumer.lookup_id = voting.room.id
    token = "tkn"
    with patch("ws.actions.RoomCacheService") as mock_room_cache_cls, \
         patch("ws.actions.UserSessionService") as mock_user_session_cls, \
         patch("ws.actions.JWTService") as mock_jwt_cls, \
         patch("ws.actions.check_voting_finish") as mock_check_finish, \
         patch("ws.actions.voting_results") as mock_voting_results:

        mock_cache = mock_room_cache_cls.return_value
        mock_cache.get_users_by_role.return_value = ["uA"]
        mock_cache.get_votes.return_value = {"uA": 5}

        mock_user_session = mock_user_session_cls.return_value
        mock_user_session.get_user_session_data.return_value = {"user_uuid": "uA"}

        mock_check_finish.return_value = True

        with patch.object(SubmitVoteAction, "get_object", return_value=voting):
            res = await SubmitVoteAction.execute(consumer, {"token": token, "vote": "5"})
            assert res["type"] == "results"
            assert res["average_score"] == voting.average_score
            assert "votes" in res

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_change_voting_status_invalid_status_returns_none(voting):
    consumer = MagicMock()
    consumer.lookup_id = voting.room.id
    with patch.object(ChangeVotingStatus, "get_object", return_value=voting):
        res = await ChangeVotingStatus.execute(consumer, {"status": "invalid_status"})
        assert res is None

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_change_voting_status_next_calls_end_voting_without_clearing_room():
    consumer = MagicMock()
    consumer.lookup_id = 1
    with patch("ws.actions.end_voting_without_clearing_room") as mock_end, \
         patch("ws.actions.Voting") as mock_voting_model:

        class M:
            pass
        mock_voting_qs = MagicMock()
        mock_voting_qs.first.return_value = M()
        mock_voting_model.objects.filter.return_value = mock_voting_qs

        res = await ChangeVotingStatus.execute(consumer, {"status": "next"})
        mock_end.assert_called_once()
        assert res == {"type": "voting_change_status", "status": "next"}
