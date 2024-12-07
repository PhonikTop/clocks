from rest_framework import serializers

from .models import Room


class RoomNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ["id", "name"]


class RoomDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ["id", "name", "is_active"]

