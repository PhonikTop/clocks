from meetings.models import Meeting
from rest_framework import serializers

from rooms.models import Room


class RoomNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ["id", "name"]


class RoomDetailSerializer(serializers.ModelSerializer):
    active_meeting_id = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ["id", "name", "active_meeting_id", "is_active"]

    def get_active_meeting_id(self, obj) -> int | None:
        meeting = Meeting.objects.filter(
            room=obj,
            active=True,
        ).first()
        return meeting.id if meeting else None
