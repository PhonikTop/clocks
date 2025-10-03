import structlog
from rooms.services.room_cache_service import RoomCacheService
from rooms.services.room_online_tracker import RoomOnlineTracker
from users.enums import UserRole

logger = structlog.get_logger()

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
    logger.info("Подведены итоги голосования", room=voting.room.id, voting=voting.id, average_score=voting.average_score, results_votes=voting.votes)

def check_voting_finish(voting_room_id) -> bool:
    voting_room = RoomCacheService(voting_room_id)
    participants = voting_room.get_users_by_role(UserRole.VOTER)
    votes = voting_room.get_votes()
    msg = len(participants) == len(votes) if participants != 0 else False
    return msg
