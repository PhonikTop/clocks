from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from meetings.models import Meeting


class VoteDetailSerializer(serializers.Serializer):
    nickname = serializers.CharField()
    vote = serializers.IntegerField()


class VotesResponseField(serializers.DictField):
    child = VoteDetailSerializer()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.read_only = True


class MeetingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ["id", "room", "task_name"]

    def validate(self, data):
        room = data.get("room")
        if room and Meeting.objects.filter(room=room, active=True).exists():
            raise ValidationError({"error": "Room meeting already exists"})
        return data


class MeetingInfoSerializer(serializers.ModelSerializer):
    votes = VotesResponseField(required=False)

    class Meta:
        model = Meeting
        fields = ["id", "room", "task_name", "votes", "average_score", "active"]


class MeetingUpdateTaskNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ["task_name"]


class MeetingRemoveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ["id"]


class MeetingResultsSerializer(serializers.ModelSerializer):
    votes = VotesResponseField(required=False)

    class Meta:
        model = Meeting
        fields = ["id", "votes", "average_score"]
        read_only_fields = ["average_score", "votes"]
