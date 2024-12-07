from django.db import transaction
from rooms.redis_client import clear_room_participants

from .redis_client import delete_votes, get_votes


def end_meeting(meeting):
    meeting.active = False
    clear_room_participants(meeting.room.id)
    with transaction.atomic():
        meeting.room.save()
        meeting.save()


def meeting_results(meeting):
    votes = get_votes(meeting.id)

    meeting.average_score = round(sum(map(int, votes.values())) / len(votes) or 0)
    meeting.votes = votes
    meeting.save()

    delete_votes(meeting)
