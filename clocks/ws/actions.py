from asgiref.sync import sync_to_async
from meetings.logic import meeting_results
from meetings.models import Meeting
from rooms.redis_client import RoomCacheManager

from .base_action import BaseAction
from .handlers import ActionHandler


class SubmitVoteAction(BaseAction):

    async def get_queryset(self):
        return Meeting.objects.filter(room=self.consumer.lookup_id, active=True)

    async def perform_action(self):
        user_name = await self.get_param("user_id")
        try:
            vote = int(await self.get_param("vote"))
        except (ValueError, TypeError):
            return {"error": "Invalid vote"}

        meeting = await self.get_object()
        room_cache = RoomCacheManager(self.consumer.lookup_id)

        participants = await sync_to_async(room_cache.get_users_by_role)("voter")
        votes = await sync_to_async(room_cache.get_votes)()

        if user_name not in participants:
            return {"error": "Participant not found"}
        if user_name in votes:
            return {"error": "Participant already voted"}

        await sync_to_async(room_cache.set_vote)(user_name, vote)

        if len(participants) == len(votes) + 1:
            votes = await sync_to_async(room_cache.get_votes)()
            await sync_to_async(meeting_results)(meeting)
            return {"votes": votes, "average_score": meeting.average_score}

        return {"status": "Vote recorded", "user": "user_name"}


action_handler = ActionHandler()
action_handler.register("submit_vote", SubmitVoteAction)
