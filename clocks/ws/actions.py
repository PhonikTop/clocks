from asgiref.sync import sync_to_async
from meetings.logic import meeting_results
from meetings.models import Meeting
from rooms.services.room_cache_service import RoomCacheService

from .base_action import BaseAction
from .handlers import ActionHandler


class SubmitVoteAction(BaseAction):
    async def get_queryset(self):
        return Meeting.objects.filter(room=self.consumer.lookup_id, active=True).select_related()

    async def perform_action(self):
        user_id = await self.get_param("user_id")
        try:
            vote = int(await self.get_param("vote"))
        except (ValueError, TypeError):
            return {"error": "Invalid vote format"}

        meeting = await self.get_object()
        room_cache = RoomCacheService(self.consumer.lookup_id)

        participants, votes = await sync_to_async(
            lambda: (room_cache.get_users_by_role("voter"), room_cache.get_votes())
        )()

        if user_id not in participants:
            return {"error": "Participant not found"}
        if user_id in votes:
            return {"error": "Participant already voted"}

        await sync_to_async(room_cache.set_vote)(user_id, vote)

        if len(participants) == len(votes) + 1:
            votes = await sync_to_async(room_cache.get_votes)()
            await sync_to_async(meeting_results)(meeting)
            return {
                "votes": votes,
                "average_score": meeting.average_score,
            }

        return {"type": "user_voted", "user": user_id}


action_handler = ActionHandler()
action_handler.register("submit_vote", SubmitVoteAction)
