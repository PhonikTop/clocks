import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.shortcuts import get_object_or_404
from meetings.models import Meeting
from meetings.serializers import MeetingSerializer
from rooms.models import Room


class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        await self.close()

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            action = text_data_json.get("action")

            if action == "refresh_participants":
                await self.send_response(await self.get_data())

            elif action == "submit_vote":
                user_id = text_data_json.get("user_id")
                vote = text_data_json.get("vote")
                await self.save_vote(user_id, vote)
            else:
                await self.send_response({"message": "unknown action"})
        except json.JSONDecodeError:
            await self.send_response({"message": "Invalid JSON format"})

    async def send_response(self, data):
        await self.send(text_data=json.dumps(data))

    @sync_to_async
    def get_meeting(self):
        return get_object_or_404(Meeting, id=1)

    @sync_to_async
    def get_room(self, meeting_id):
        return get_object_or_404(Room, current_meeting=meeting_id)

    async def get_data(self):
        meeting = await self.get_meeting()
        serializer = MeetingSerializer(meeting, fields=["votes"])
        return serializer.data

    @sync_to_async
    def save_vote_sync(self, user_name, vote):
        meeting: Meeting = Meeting.objects.get(id=1)
        meeting.votes[user_name] = vote
        meeting.save()

    async def save_vote(self, user_name, vote):
        meeting: Meeting = await self.get_meeting()
        room = await self.get_room(meeting.id)

        if not any(user_name in d for d in room.users):
            await self.send_response({"error": "Participant doesn't exist"})
        else:
            await self.save_vote_sync(user_name, vote)
            await self.send_response({"success": "Vote saved successfully"})
