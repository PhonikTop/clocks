import json
from unittest.mock import patch

import pytest
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator

from ws.consumers import RoomConsumer


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_connect_accepts_and_sends_results_if_meeting_with_avg(room_url_router, finished_meeting):
    room_id = finished_meeting.room.id
    token = "dummy-token"

    with patch.object(RoomConsumer, "_get_lookup_id", return_value=room_id), \
         patch.object(RoomConsumer, "_get_user_uuid", return_value=token), \
         patch("ws.consumers.RoomMessageService") as mock_room_message_service_cls, \
         patch("ws.consumers.UserChannelTracker") as mock_user_channel_tracker_cls, \
         patch("ws.consumers.RoomOnlineTracker") as mock_room_online_tracker_cls, \
         patch("ws.consumers.RoomCacheService") as mock_room_cache_cls:

        mock_room_cache = mock_room_cache_cls.return_value
        mock_room_cache.get_votes.return_value = {"user-uuid-1": 5}

        with patch.object(RoomConsumer, "get_meeting", return_value=finished_meeting):
            communicator = WebsocketCommunicator(room_url_router, f"/ws/room/{room_id}/?token={token}")
            connected, _ = await communicator.connect()
            assert connected

            msg = await communicator.receive_from()
            payload = json.loads(msg)
            assert payload["type"] == "results"
            assert payload["average_score"] == finished_meeting.average_score
            assert "votes" in payload

            await communicator.disconnect()

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_group_message_broadcasts_to_other_clients(room_url_router, room):
    room_id = room.id

    async def fake_get_lookup_id(self):
        return room_id
    async def fake_get_user_uuid(self):
        return "uuid-A"

    with patch.object(RoomConsumer, "_get_lookup_id", new=fake_get_lookup_id), \
         patch.object(RoomConsumer, "_get_user_uuid", new=fake_get_user_uuid), \
         patch("ws.consumers.RoomMessageService") as mock_room_message_service_cls, \
         patch("ws.consumers.RoomOnlineTracker") as mock_room_online_tracker_cls, \
         patch("ws.consumers.check_meeting_finish") as mock_check_finish:

        mock_check_finish.return_value = False

        comm1 = WebsocketCommunicator(room_url_router, f"/ws/room/{room_id}/?token=a")
        comm2 = WebsocketCommunicator(room_url_router, f"/ws/room/{room_id}/?token=b")

        connected1, _ = await comm1.connect()
        connected2, _ = await comm2.connect()

        assert connected1
        assert connected2

        layer = get_channel_layer()
        await layer.group_send(f"room_{room_id}", {"type": "user_voted", "user": "someone", "score": 5})

        msg1 = await comm1.receive_from()
        msg2 = await comm2.receive_from()

        payload1 = json.loads(msg1)
        payload2 = json.loads(msg2)

        assert payload1["type"] == "user_voted"
        assert payload2["type"] == "user_voted"
        assert payload1["user"] == "someone"
        assert payload2["user"] == "someone"

        await comm1.disconnect()
        await comm2.disconnect()
