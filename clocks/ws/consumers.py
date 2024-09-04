import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import get_object_or_404
from meetings.serializers import MeetingSerializer


class RoomConsumer(WebsocketConsumer):

    def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        async_to_sync(self.channel_layer.group_add)(f"room_{self.room_id}", self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(f"room_{self.room_id}", self.channel_name)

    def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            action = text_data_json.get("action")

            if action == "refresh_participants":
                response = self.get_data()
                async_to_sync(self.channel_layer.group_send)(
                    f"room_{self.room_id}",
                    {
                        "type": "chat.message",
                        "message": json.dumps(response),
                    }
                )

            elif action == "submit_vote":
                user_id = text_data_json.get("user_id")
                vote = text_data_json.get("vote")
                response = self.save_vote(user_id, vote)

                async_to_sync(self.channel_layer.group_send)(
                    f"room_{self.room_id}",
                    {
                        "type": "chat.message",
                        "message": json.dumps(response),
                    }
                )
            else:
                async_to_sync(self.channel_layer.group_send)(
                    f"room_{self.room_id}",
                    {
                        "type": "chat.message",
                        "message": json.dumps({"message": "unknown action"}),
                    }
                )
        except json.JSONDecodeError:
            async_to_sync(self.channel_layer.group_send)(
                f"room_{self.room_id}",
                {
                    "type": "chat.message",
                    "message": json.dumps({"message": "Invalid JSON format"}),
                }
            )

    def chat_message(self, event):
        self.send(text_data=event["message"])

    def get_meeting(self):
        from meetings.models import Meeting

        return get_object_or_404(Meeting, room=self.room_id)

    def get_room(self):
        from rooms.models import Room

        return get_object_or_404(Room, id=self.room_id)

    def get_data(self):
        meeting = self.get_meeting()
        serializer = MeetingSerializer(meeting, fields=["votes"])
        data = serializer.data.copy()

        if "votes" in data:
            data["votes"] = {k: v for k, v in data["votes"].items() if v is not None}

        return data

    def save_vote(self, user_name, vote):
        meeting = self.get_meeting()
        room = self.get_room()

        if not any(user_name in d for d in room.users):
            return {"error": "Participant doesn't exist"}
        else:
            meeting.votes[user_name] = vote
            meeting.save()
            return self.get_data()
