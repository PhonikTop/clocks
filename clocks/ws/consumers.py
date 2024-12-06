import json

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.shortcuts import aget_object_or_404
from meetings.logic import meeting_results
from meetings.models import Meeting
from meetings.redis_client import add_vote, get_votes
from rooms.models import Room


class BaseConsumer(AsyncWebsocketConsumer):
    model = None
    group_prefix = ""

    async def connect(self):
        self.lookup_id = await self.get_lookup_id()
        await self.channel_layer.group_add(f"{self.group_prefix}_{self.lookup_id}", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(f"{self.group_prefix}_{self.lookup_id}", self.channel_name)

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            action = text_data_json.get("action")
            if action:
                response = await getattr(self, action)(text_data_json)
                await self.send_group_message(response)
            else:
                await self.send_group_message({"message": "unknown action"})
        except json.JSONDecodeError:
            await self.send_group_message({"message": "Invalid JSON format"})

    async def send_group_message(self, message):
        await self.channel_layer.group_send(
            f"{self.group_prefix}_{self.lookup_id}",
            {
                "type": "chat.message",
                "message": json.dumps(message),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=event["message"])

    async def get_lookup_id(self):
        return self.scope["url_route"]["kwargs"]["id"]

    async def get_object(self, model, **filters):
        return await aget_object_or_404(model, **filters)

    async def save_object(self, obj):
        await database_sync_to_async(obj.save)()


class RoomConsumer(BaseConsumer):
    model = Room
    group_prefix = "room"

    async def get_lookup_id(self):
        scope = self.scope["url_route"]["kwargs"]["id"]
        exists = await Meeting.objects.filter(room_id=scope, active=True).aexists()
        if not exists:
            msg = "Meeting does not exist"
            raise AttributeError(msg)
        return scope

    async def refresh_participants(self, _):
        meeting = await self.get_object(Meeting, room=self.lookup_id, active=True)
        return meeting.votes

    async def submit_vote(self, data):
        user_name = data.get("user_id")

        try:
            vote = int(data.get("vote"))
        except ValueError:
            return {"error": "User vote invalid"}

        meeting = await self.get_object(Meeting, room=self.lookup_id, active=True)
        room = await self.get_object(Room, id=self.lookup_id)
        votes: dict = await sync_to_async(get_votes)(meeting)

        if user_name not in room.participants:
            return {"error": "Participant doesn't exist"}
        if user_name in votes:
            return {"error": "Participant already voted"}

        votes = await sync_to_async(add_vote)(meeting.id, user_name, vote)

        if len(room.participants) == len(votes):
            await sync_to_async(meeting_results)(meeting)
            await self.save_object(meeting)

            return {"votes": votes, "average_score": meeting.average_score}

        return {"voted": f"{user_name}"}

    async def user_joined(self, event):
        user = event["user"]
        role = event["role"]
        await self.send(text_data=json.dumps({
            "message": {user: role}
        }))
