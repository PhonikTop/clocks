import json
from urllib.parse import parse_qs

from api.services.jwt_service import JWTService
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from rooms.models import Room
from rooms.services.message_senders.django_channel import DjangoChannelMessageSender
from rooms.services.room_cache_service import RoomCacheService
from rooms.services.room_message_service import RoomMessageService
from users.services.user_session_service import UserSessionService

from .actions import action_handler
from rooms.services.room_online_tracker import RoomOnlineTracker
from .services.user_channel_tracker import UserChannelTracker


class RoomConsumer(AsyncWebsocketConsumer):
    group_prefix = "room"


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._room_cache_service = None
        self._jwt_service = None
        self._user_session_service = None
        self._message_sender = None
        self._room_message_service = None
        self.lookup_id = None
        self.uuid = None

    @property
    def room_cache(self):
        if self._room_cache_service is None:
            self.lookup_id = self.scope["url_route"]["kwargs"]["id"]
            self._room_cache_service = RoomCacheService(self.lookup_id)
        return self._room_cache_service

    @property
    def user_session(self):
        if self._user_session_service is None:
            self._jwt_service = JWTService()
            self._user_session_service = UserSessionService(
                self._jwt_service,
                self.room_cache
            )
        return self._user_session_service

    @property
    def message_sender(self):
        if self._message_sender is None:
            self._message_sender = DjangoChannelMessageSender()
        return self._message_sender

    @property
    def room_message_service(self):
        if self._room_message_service is None:
            self._room_message_service = RoomMessageService(
                self.lookup_id,
                self.message_sender,
                self.room_cache
            )
        return self._room_message_service

    async def connect(self):
        self.lookup_id = await self._get_lookup_id()
        self.uuid = await self._get_user_uuid()
        if not self.lookup_id or not self.uuid:
            await self.close()
            return

        await self.channel_layer.group_add(self._group_name, self.channel_name)
        await self.accept()

        await sync_to_async(UserChannelTracker.add_participant)(self.channel_name, self.uuid, self.lookup_id)
        await sync_to_async(RoomOnlineTracker.set_user_online)(self.uuid, self.lookup_id)

        await sync_to_async(self.room_message_service.send_room_voted_users)()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self._group_name, self.channel_name)
        if self.lookup_id or self.uuid:
            await sync_to_async(RoomOnlineTracker.set_user_offline)(self.uuid, self.lookup_id)
            await sync_to_async(UserChannelTracker.remove_participant)(self.channel_name)

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            action_name = text_data_json.get("action")
            response = await action_handler.execute(action_name, self, text_data_json)
            await self.send(text_data=json.dumps(response))
        except json.JSONDecodeError:
            await self.send({"error": "Invalid JSON format"})

    @property
    def _group_name(self):
        return f"{self.group_prefix}_{self.lookup_id}"

    async def _get_lookup_id(self):
        scope_id = self.scope["url_route"]["kwargs"].get("id")
        if await Room.objects.filter(id=scope_id, is_active=True).aexists():
            return int(scope_id)
        return None

    async def _get_user_uuid(self):
        query_string = self.scope["query_string"].decode("utf-8", errors="ignore")
        query_params = parse_qs(query_string)
        token = query_params.get("token", [None])[0]

        if token is None:
            return None

        user_data = await sync_to_async(self.user_session.get_user_session_data)(token)
        uuid_value = user_data["user_uuid"]
        if not uuid_value:
            return None

        return uuid_value

    async def user_joined(self, event):
        await self.send(text_data=json.dumps(event))

    async def task_name_changed(self, event):
        await self.send(text_data=json.dumps(event))

    async def meeting_started(self, event):
        await self.send(text_data=json.dumps(event))

    async def voted_users_update(self, event):
        await self.send(text_data=json.dumps(event))

    async def meeting_change_status(self, event):
        await self.send(text_data=json.dumps(event))

    async def user_online(self, event):
        await self.send(text_data=json.dumps(event))

    async def user_offline(self, event):
        await self.send(text_data=json.dumps(event))

