from asgiref.sync import sync_to_async
from meetings.logic import meeting_results, end_meeting_without_clearing_room
from meetings.models import Meeting
from rooms.services.room_cache_service import RoomCacheService
from rooms.services.room_message_service import RoomStatusType
from users.services.user_session_service import UserSessionService
from api.services.jwt_service import JWTService

from .base_action import BaseAction
from .handlers import ActionHandler


class SubmitVoteAction(BaseAction):
    def get_queryset(self):
        return Meeting.objects.filter(room=self.consumer.lookup_id, active=True)

    async def perform_action(self):
        token = await self.get_param("token")
        try:
            vote = int(await self.get_param("vote"))
        except (ValueError, TypeError):
            return {"error": "Invalid vote format"}

        meeting = await self.get_object()
        jwt_service = JWTService()
        room_cache = RoomCacheService(self.consumer.lookup_id)
        user_session_service = UserSessionService(jwt_service, room_cache)

        user_id = user_session_service.get_user_session_data(token)["user_uuid"]
        participants = await sync_to_async(
            room_cache.get_users_by_role
        )("voter")

        if user_id not in participants:
            return {"error": "Participant not found"}

        await sync_to_async(room_cache.set_vote)(user_id, vote)

        votes = await sync_to_async(
            room_cache.get_votes
        )()

        if len(participants) == len(votes):
            votes = await sync_to_async(room_cache.get_votes)()
            await sync_to_async(meeting_results)(meeting)
            return {
                "type": "results",
                "votes": votes,
                "average_score": meeting.average_score,
            }

        return {"type": "user_voted", "user": user_id}

class ChangeMeetingStatus(BaseAction):
    def get_queryset(self):
        return Meeting.objects.filter(room=self.consumer.lookup_id, active=True)

    async def perform_action(self):
        meeting = await self.get_object()

        new_status = await self.get_param("status")
        if new_status not in [s.value for s in RoomStatusType]:
            return None

        if new_status == RoomStatusType.NEXT.value:
            await sync_to_async(end_meeting_without_clearing_room)(meeting)

        return {
            "type": "meeting_change_status",
            "status": new_status
        }


action_handler = ActionHandler()
action_handler.register("submit_vote", SubmitVoteAction)
action_handler.register("change_meeting_status", ChangeMeetingStatus)
