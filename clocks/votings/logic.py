from rooms.services.room_cache_service import RoomCacheService
from rooms.services.room_online_tracker import RoomOnlineTracker
from users.enums import UserRole


def end_voting(voting):
    voting_room = RoomCacheService(voting.room.id)
    voting.active = False
    voting_room.clear_room()
    RoomOnlineTracker.clean_room_offline_participants(voting.room.id)
    voting.save()


def end_voting_without_clearing_room(voting):
    voting_room = RoomCacheService(voting.room.id)
    voting.active = False
    voting_room.clear_votes()
    voting.save()


def voting_results(voting):
    voting_room = RoomCacheService(voting.room.id)
    votes = voting_room.get_votes()
    voting.average_score = (
        -(-sum(item["vote"] for item in votes.values()) // len(votes))
        if votes
        else 0
    )
    voting.votes = votes
    voting.save()

def check_voting_finish(voting_room_id) -> bool:
    voting_room = RoomCacheService(voting_room_id)
    participants = voting_room.get_users_by_role(UserRole.VOTER)
    votes = voting_room.get_votes()
    msg = len(participants) == len(votes) if participants != 0 else False
    return msg
