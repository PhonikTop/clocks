from rest_framework import serializers

from users.enums import UserRole


class UserInfoSerializer(serializers.Serializer):
    nickname = serializers.CharField(max_length=25)
    role = serializers.ChoiceField(choices=UserRole.choices())

class UserFullInfoSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=UserRole.choices())
    nickname = serializers.CharField(max_length=25)
    user_uuid = serializers.CharField()
