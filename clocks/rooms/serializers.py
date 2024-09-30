from rest_framework import serializers

from clocks.room.models import Room


class RoomNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ["id", "name"]


class RoomDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ["id", "name", "is_active", "participants", "current_meeting_id"]


class RoomParticipantsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ["participants"]
