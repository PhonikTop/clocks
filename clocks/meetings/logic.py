from rooms.redis_client import RoomCacheManager


def end_meeting(meeting):
    meeting_room = RoomCacheManager(meeting.room.id)
    meeting.active = False
    meeting_room.clear_room()
    meeting.save()


def meeting_results(meeting):
    meeting_room = RoomCacheManager(meeting.room.id)
    votes = meeting_room.get_votes()
    meeting.average_score = round(
        sum(item["vote"] for item in votes.values()) / len(votes) or 0
    )
    meeting.votes = votes
    meeting.save()
