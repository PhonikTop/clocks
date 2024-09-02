import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import get_object_or_404
from meetings.models import Meeting
from meetings.serializers import MeetingSerializer
from rooms.models import Room


class RoomConsumer(WebsocketConsumer):
    def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.group_name = f"room_{self.room_id}"
        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.group_name, self.channel_name)

    def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get("action")
            response = {"message": "unknown action"}

            if action == "refresh_participants":
                response = self.get_data()
            elif action == "submit_vote":
                response = self.save_vote(data.get("user_id"), data.get("vote"))

            self.send_group_message(response)
        except json.JSONDecodeError:
            self.send_group_message({"message": "Invalid JSON format"})

    def send_group_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {"type": "chat.message", "message": json.dumps(message)},
        )

    def get_meeting(self):
        return get_object_or_404(Meeting, room_id=self.room_id)

    def get_data(self):
        meeting = self.get_meeting()
        serializer = MeetingSerializer(meeting, fields=["votes"])
        data = serializer.data
        data["votes"] = {k: v for k, v in data.get("votes", {}).items() if v is not None}
        return data

    def save_vote(self, user_name, vote):
        meeting = self.get_meeting()
        room = get_object_or_404(Room, id=self.room_id)

        if not any(user_name in d for d in room.users):
            return {"error": "Participant doesn't exist"}

        meeting.votes[user_name] = vote
        meeting.save()
        return self.get_data()
