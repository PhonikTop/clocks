from meetings.models import Meeting
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.db import models

class UserRoleChoices(models.TextChoices):
    OBSERVER = 'observer', 'Observer'
    VOTER = 'voter', 'Voter'

class UserInputSerializer(serializers.Serializer):
    nickname = serializers.CharField(max_length=25)
    role = serializers.ChoiceField(choices=UserRoleChoices.choices)

    def validate(self, data):
        room = self.context.get("room")
        if not room:
            raise ValidationError({"error": "Room instance is required in context"})

        current_meeting = Meeting.objects.filter(room_id=room.id, active=True).first()
        if not current_meeting:
            raise ValidationError({"error": "No active meeting in the room"})

        return data
