from django.db import transaction


def end_meeting(meeting):
    meeting.active = False
    meeting.room.current_meeting = None
    meeting.room.participants = []
    with transaction.atomic():
        meeting.room.save()
        meeting.save()


def meeting_results(meeting):
    valid_votes = list(filter(None, meeting.votes.values()))
    meeting.average_score = (
        round(sum(map(int, valid_votes)) / len(valid_votes)) if valid_votes else 0
    )
    meeting.save()
