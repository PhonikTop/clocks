from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from votings.models import Voting


class VoteDetailSerializer(serializers.Serializer):
    nickname = serializers.CharField()
    vote = serializers.IntegerField()


class VotesResponseField(serializers.DictField):
    child = VoteDetailSerializer()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.read_only = True


class VotingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voting
        fields = ["id", "room", "task_name"]

    def validate(self, data):
        room = data.get("room")
        if room and Voting.objects.filter(room=room, active=True).exists():
            raise ValidationError({"error": "Room voting already exists"})
        return data


class VotingInfoSerializer(serializers.ModelSerializer):
    votes = VotesResponseField(required=False)

    class Meta:
        model = Voting
        fields = ["id", "room", "task_name", "votes", "average_score", "active"]


class VotingUpdateTaskNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voting
        fields = ["task_name"]


class VotingRemoveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voting
        fields = ["id"]


class VotingResultsSerializer(serializers.ModelSerializer):
    votes = VotesResponseField(required=False)

    class Meta:
        model = Voting
        fields = ["id", "votes", "average_score"]
        read_only_fields = ["average_score", "votes"]
