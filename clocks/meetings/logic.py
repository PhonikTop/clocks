from rooms.services.room_cache_service import RoomCacheService
from rooms.services.room_online_tracker import RoomOnlineTracker
from users.enums import UserRole


def end_meeting(meeting):
    meeting_room = RoomCacheService(meeting.room.id)
    meeting.active = False
    meeting_room.clear_room()
    RoomOnlineTracker.clean_room_offline_participants(meeting.room.id)
    meeting.save()


def end_meeting_without_clearing_room(meeting):
    meeting_room = RoomCacheService(meeting.room.id)
    meeting.active = False
    meeting_room.clear_votes()
    meeting.save()


def meeting_results(meeting):
    meeting_room = RoomCacheService(meeting.room.id)
    votes = meeting_room.get_votes()
    meeting.average_score = (
        -(-sum(item["vote"] for item in votes.values()) // len(votes))
        if votes
        else 0
    )
    meeting.votes = votes
    meeting.save()

def check_meeting_finish(meeting_room_id) -> bool:
    meeting_room = RoomCacheService(meeting_room_id)
    participants = meeting_room.get_users_by_role(UserRole.VOTER)
    votes = meeting_room.get_votes()
    msg = len(participants) == len(votes) if participants != 0 else False
    return msg
