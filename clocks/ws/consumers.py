import json

from channels.generic.websocket import AsyncWebsocketConsumer
from meetings.models import Meeting

from .actions import action_handler


class RoomConsumer(AsyncWebsocketConsumer):
    group_prefix = "room"

    async def connect(self):
        self.lookup_id = await self._get_lookup_id()
        if self.lookup_id:
            await self.channel_layer.group_add(self._group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self._group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            action_name = text_data_json.get("action")
            response = await action_handler.execute(action_name, self, text_data_json)
            await self._send_group_message(response)
        except json.JSONDecodeError:
            await self._send_group_message({"error": "Invalid JSON format"})

    @property
    def _group_name(self):
        return f"{self.group_prefix}_{self.lookup_id}"

    async def _get_lookup_id(self):
        scope_id = self.scope["url_route"]["kwargs"].get("id")
        if await Meeting.objects.filter(room_id=scope_id, active=True).aexists():
            return scope_id
        return None

    async def _send_group_message(self, message):
        await self.channel_layer.group_send(
            self._group_name,
            {
                "type": "chat.message",
                "message": json.dumps(message),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=event["message"])
