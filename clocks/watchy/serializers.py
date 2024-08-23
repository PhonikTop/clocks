from rest_framework import serializers

from .models import Room, Session, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "nickname", "room", "is_observer", "state"]


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ["id", "name", "is_active"]


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ["id", "room", "task_name", "votes", "average_score", "status"]
