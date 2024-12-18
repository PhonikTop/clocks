from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Meeting


class MeetingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ["id", "room", "task_name"]

    def validate(self, data):
        room = data.get("room")
        if room and Meeting.objects.filter(room=room, active=True).exists():
            raise ValidationError({"error": "Room meeting already exists"})
        return data


class MeetingGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ["id", "room", "task_name", "votes", "average_score", "active"]


class MeetingUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ["task_name"]


class MeetingRemoveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ["id"]


class MeetingResultsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ["id", "votes"]
        read_only_fields = ["average_score"]


class MeetingVotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ["votes"]


class MeetingHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ["id", "task_name", "votes", "average_score"]
