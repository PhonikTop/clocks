from rooms.services.room_cache_service import RoomCacheService
from ws.services.room_online_tracker import RoomOnlineTracker

def end_meeting(meeting):
    meeting_room = RoomCacheService(meeting.room.id)
    meeting.active = False
    meeting_room.clear_room()
    RoomOnlineTracker.clean_room_participant(meeting.room.id)
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
        round(sum(item["vote"] for item in votes.values()) / len(votes))
        if votes
        else 0
    )
    meeting.votes = votes
    meeting.save()
