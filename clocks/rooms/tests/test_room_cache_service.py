import random
from uuid import uuid4

import pytest
from meetings.models import Meeting
from users.enums import UserRole

from rooms.services.room_cache_service import RoomCacheService


def test_add_and_get_user(fake_cache, room):
    rcs = RoomCacheService(room.name)
    user_id = str(uuid4())

    rcs.add_user(user_id, role=UserRole.VOTER, nickname="alice")
    got = rcs.get_user(user_id)

    assert got is not None
    assert got["nickname"] == "alice"
    assert got["role"] == UserRole.VOTER

    room_users = rcs.get_room_users()
    assert user_id in room_users
    assert room_users[user_id]["nickname"] == "alice"

def test_add_existing_user_raises(fake_cache, room):
    rcs = RoomCacheService(room.name)
    user_id = str(uuid4())
    rcs.add_user(user_id, role=UserRole.VOTER)
    with pytest.raises(ValueError):
        rcs.add_user(user_id, role=UserRole.VOTER)

def test_remove_user(fake_cache, room):
    rcs = RoomCacheService(room.name)
    user_id = str(uuid4())
    rcs.add_user(user_id, role=UserRole.OBSERVER)
    assert rcs.get_user(user_id) is not None

    rcs.remove_user(user_id)
    assert rcs.get_user(user_id) is None
    assert user_id not in rcs.get_room_users()

def test_get_users_by_role(fake_cache, room):
    rcs = RoomCacheService(room.name)
    u1 = str(uuid4())
    u2 = str(uuid4())
    rcs.add_user(u1, role=UserRole.VOTER)
    rcs.add_user(u2, role=UserRole.OBSERVER)

    voters = rcs.get_users_by_role(UserRole.VOTER)
    assert u1 in voters
    assert u2 not in voters

def test_set_vote_success_and_invalid(fake_cache, room):
    rcs = RoomCacheService(room.name)
    uid_voter = "voter-1"
    uid_observer = "admin-1"

    rcs.add_user(uid_voter, role=UserRole.VOTER, nickname="V")
    rcs.add_user(uid_observer, role=UserRole.OBSERVER, nickname="A")

    rcs.set_vote(uid_voter, 5)
    votes = rcs.get_votes()
    assert uid_voter in votes
    assert votes[uid_voter]["vote"] == 5
    assert votes[uid_voter]["nickname"] == "V"

    with pytest.raises(ValueError):
        rcs.set_vote(uid_observer, 1)

def test_remove_user_vote_and_clear_votes(fake_cache, room):
    rcs = RoomCacheService(room.name)
    uid = str(uuid4())
    rcs.add_user(uid, role=UserRole.VOTER, nickname="Vin")
    rcs.set_vote(uid, 3)
    assert uid in rcs.get_votes()

    rcs.remove_user_vote(uid)
    assert uid not in rcs.get_votes()

    rcs.set_vote(uid, 3)
    rcs.clear_votes()
    assert rcs.get_votes() == {}

def test_transfer_user_moves_user_and_vote_to_target(fake_cache):
    src = RoomCacheService("room-src")
    tgt_room_id = "room-tgt"
    uid = str(uuid4())

    src.add_user(uid, role=UserRole.VOTER, nickname="Tr")
    src.set_vote(uid, 3)

    assert uid in src.get_votes()

    src.transfer_user(uid, tgt_room_id)

    tgt = RoomCacheService(tgt_room_id)
    assert tgt.get_user(uid) is not None

    assert uid in tgt.get_votes()
    assert uid not in src.get_votes()

def test_clear_room_deletes_all(fake_cache, room):
    rcs = RoomCacheService(room.name)
    u1 = str(uuid4())
    u2 = str(uuid4())
    rcs.add_user(u1, role=UserRole.VOTER)
    rcs.add_user(u2, role=UserRole.OBSERVER)
    rcs.set_vote(u1, 1)

    rcs.clear_room()

    assert rcs.get_room_users() == {}
    assert rcs.get_votes() == {}
    assert rcs.get_user(u1) is None
    assert rcs.get_user(u2) is None

def test_start_and_get_meeting_timer(fake_cache, room):
    rcs = RoomCacheService(room.id)
    minutes = random.randint(10, 15)  # noqa: S311
    rcs.start_meeting_timer(minutes)

    assert rcs.get_meeting_timer() == minutes
