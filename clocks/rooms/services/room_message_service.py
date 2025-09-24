from enum import Enum

from rooms.services.message_senders.base import MessageSender
from rooms.services.room_cache_service import RoomCacheService, UserData


class RoomStatusType(Enum):
    RESTART = "restart"
    END = "ended"
    NEXT = "next"

class RoomMessageService:
    def __init__(self, room_id: int, message_sender: MessageSender, room_cache_service: RoomCacheService | None = None):
        self.room_id = room_id
        self.message_sender = message_sender
        self._room_cache_service = room_cache_service

    @property
    def room_cache_service(self):
        if self._room_cache_service is None:
            raise ValueError("room_cache_service is missing")
        return self._room_cache_service

    @property
    def _group_name(self):
        return f"room_{self.room_id}"

    def notify_meeting_restart(self):
        message = {
            "type": "meeting_change_status",
            "status": RoomStatusType.RESTART.value
        }
        self.message_sender.send(self._group_name, message)

    def notify_user_joined(self, uuid: str) -> str | None:
        """
        Уведомляет о присоединении пользователя к комнате.

        Args:
            uuid (str) : Идентификатор пользователя.
        """
        user_data: UserData = self.room_cache_service.get_user(uuid)

        message = {
            "type": "user_joined",
            "user": {uuid: user_data}
        }
        self.message_sender.send(self._group_name, message)

    def notify_user_kicked(self, kicked_uuid: str, kicker_uuid: str):
        kicked_user_data: UserData = self.room_cache_service.get_user(kicked_uuid)
        kicker_user_data: UserData = self.room_cache_service.get_user(kicker_uuid)

        message = {
            "type": "user_kicked",
            "kicked": {kicked_uuid: kicked_user_data},
            "kicker": {kicker_uuid: kicker_user_data},
        }

        self.message_sender.send(self._group_name, message)

    def notify_room_timer_started(self, timer_end_time: float, timer_started_user_uuid: str):
        timer_started_user_data: UserData = self.room_cache_service.get_user(timer_started_user_uuid)

        message = {
            "type": "timer_started",
            "end_time": timer_end_time,
            "timer_started_user": {timer_started_user_uuid: timer_started_user_data},
        }

        self.message_sender.send(self._group_name, message)

    def notify_room_timer_reset(self, timer_reset_user_uuid: str):
        timer_reset_user_data: UserData = self.room_cache_service.get_user(timer_reset_user_uuid)

        message = {
            "type": "timer_reset",
            "timer_reset_user": {timer_reset_user_uuid: timer_reset_user_data},
        }

        self.message_sender.send(self._group_name, message)

    def notify_meeting_results(self, votes, average_score):
        message = {
            "type": "results",
            "votes": votes,
            "average_score": average_score,
        }
        self.message_sender.send(self._group_name, message)

    def notify_user_offline(self, user_uuid):
        user_data: UserData = self.room_cache_service.get_user(user_uuid)

        message = {
            "type": "user_offline",
            "user": {user_uuid: user_data}
        }
        self.message_sender.send(self._group_name, message)

    def notify_user_online(self, user_uuid):
        user_data: UserData = self.room_cache_service.get_user(user_uuid)

        message = {
            "type": "user_online",
            "user": {user_uuid: user_data}
        }
        self.message_sender.send(self._group_name, message)

    def send_room_voted_users(self):
        votes = self.room_cache_service.get_votes()

        message = {
            "type": "voted_users_update",
            "voted_users": list(votes.keys())
        }
        self.message_sender.send(self._group_name, message)

    def notify_meeting_task_name_changed(self, new_task_name:str, user_nickname: str):
        message = {
            "type": "task_name_changed",
            "new_task_name": new_task_name,
            "user": user_nickname
        }
        self.message_sender.send(self._group_name, message)

    def notify_meeting_started(self, meeting_id: int):
        message = {
            "type": "meeting_started",
            "id": meeting_id,
        }
        self.message_sender.send(self._group_name, message)
