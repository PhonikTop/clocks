import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.shortcuts import get_object_or_404
from meetings.models import Meeting
from meetings.serializers import MeetingSerializer
from rooms.models import Room


class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.group_name = f"room_{self.room_id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get("action")
            response = {"message": "unknown action"}

            if action == "refresh_participants":
                response = await self.get_data()
            elif action == "submit_vote":
                user_id = data.get("user_id")
                vote = data.get("vote")
                response = await self.save_vote(user_id, vote)

            await self.send_group_message(response)
        except json.JSONDecodeError:
            await self.send_group_message({"message": "Invalid JSON format"})

    async def send_group_message(self, message):
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat.message",
                "message": json.dumps(message),
            }
        )

    @sync_to_async
    def get_meeting_sync(self):
        return get_object_or_404(Meeting, room_id=self.room_id)

    async def get_meeting(self):
        return await self.get_meeting_sync()

    async def get_data(self):
        meeting = await self.get_meeting()
        serializer = MeetingSerializer(meeting, fields=["votes"])
        data = serializer.data
        data["votes"] = {k: v for k, v in data.get("votes", {}).items() if v is not None}
        return data

    @sync_to_async
    def save_vote_sync(self, user_name, vote):
        meeting = get_object_or_404(Meeting, room_id=self.room_id)
        room = get_object_or_404(Room, id=self.room_id)

        if not any(user_name in d for d in room.users):
            return {"error": "Participant doesn't exist"}

        meeting.votes[user_name] = vote
        meeting.save()

        serializer = MeetingSerializer(meeting, fields=["votes"])
        data = serializer.data
        data["votes"] = {k: v for k, v in data.get("votes", {}).items() if v is not None}
        return data

    async def save_vote(self, user_name, vote):
        return await self.save_vote_sync(user_name, vote)

    async def chat_message(self, event):
        message = event["message"]

        await self.send(text_data=message)
