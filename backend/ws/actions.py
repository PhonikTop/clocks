import structlog
from api.services.jwt_service import JWTService
from asgiref.sync import sync_to_async
from rooms.services.room_cache_service import RoomCacheService
from rooms.services.room_message_service import RoomStatusType
from users.enums import UserRole
from users.services.user_session_service import UserSessionService
from votings.logic import (
    check_voting_finish,
    end_voting_without_clearing_room,
    voting_results,
)
from votings.models import Voting

from ws.base_action import BaseAction

from .handlers import ActionHandler

logger = structlog.get_logger()

class SubmitVoteAction(BaseAction):
    def get_queryset(self):
        return Voting.objects.filter(room=self.consumer.lookup_id, active=True)

    async def perform_action(self):
        token = await self.get_param("token")
        try:
            vote = int(await self.get_param("vote"))
        except (ValueError, TypeError):
            return {"error": "Invalid vote format"}

        voting = await self.get_object()
        jwt_service = JWTService()
        room_cache = RoomCacheService(self.consumer.lookup_id)
        user_session_service = UserSessionService(jwt_service, room_cache)

        user_id = user_session_service.get_user_session_data(token)["user_uuid"]
        participants = await sync_to_async(
            room_cache.get_users_by_role
        )(UserRole.VOTER)

        if user_id not in participants:
            return {"error": "Participant not found"}

        await sync_to_async(room_cache.set_vote)(user_id, vote)
        logger.info("Пользователь проголосовал", room=self.consumer.lookup_id, voting=voting.id, user=user_id, vote=vote)

        voting_finished: bool = await sync_to_async(check_voting_finish)(self.consumer.lookup_id)

        if voting_finished:
            votes = await sync_to_async(room_cache.get_votes)()
            await sync_to_async(voting_results)(voting)
            return {
                "type": "results",
                "votes": votes,
                "average_score": voting.average_score,
            }

        return {"type": "user_voted", "user": user_id}

class ChangeVotingStatus(BaseAction):
    def get_queryset(self):
        return Voting.objects.filter(room=self.consumer.lookup_id, active=True)

    async def perform_action(self):
        voting = await self.get_object()
        user_uuid = await self.get_param("user_uuid")

        new_status = await self.get_param("status")
        if new_status not in [s.value for s in RoomStatusType]:
            return None

        if new_status == RoomStatusType.NEXT.value:
            await sync_to_async(end_voting_without_clearing_room)(voting)
        logger.info("Статус голосования изменен", room=self.consumer.lookup_id, voting=voting.id, user=user_uuid)
        return {
            "type": "voting_change_status",
            "status": new_status
        }


action_handler = ActionHandler()
action_handler.register("submit_vote", SubmitVoteAction)
action_handler.register("change_voting_status", ChangeVotingStatus)
