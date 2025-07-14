from rest_framework import serializers

from users.enums import UserRole


class UserInputSerializer(serializers.Serializer):
    nickname = serializers.CharField(max_length=25)
    role = serializers.ChoiceField(choices=UserRole.choices())

class UserFullInfoSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=UserRole.choices())
    nickname = serializers.CharField(max_length=25)
    vote = serializers.IntegerField(allow_null=True)
    user_uuid = serializers.UUIDField()
