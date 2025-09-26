from rest_framework import serializers
from votings.models import Voting

from rooms.models import Room


class RoomNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ["id", "name"]


class RoomDetailSerializer(serializers.ModelSerializer):
    active_voting_id = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ["id", "name", "active_voting_id", "active"]

    def get_active_voting_id(self, obj) -> int | None:
        voting = Voting.objects.filter(
            room=obj,
            active=True,
        ).first()
        return voting.id if voting else None
