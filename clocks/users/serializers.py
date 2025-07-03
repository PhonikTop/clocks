from django.db import models
from rest_framework import serializers


class UserRoleChoices(models.TextChoices):
    OBSERVER = "observer", "Observer"
    VOTER = "voter", "Voter"

class UserInputSerializer(serializers.Serializer):
    nickname = serializers.CharField(max_length=25)
    role = serializers.ChoiceField(choices=UserRoleChoices.choices)

class UserFullInfoSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=UserRoleChoices.choices)
    nickname = serializers.CharField(max_length=25)
    vote = serializers.IntegerField(allow_null=True)
    user_uuid = serializers.UUIDField()
