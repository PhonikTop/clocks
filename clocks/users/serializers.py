from rest_framework import serializers


class UserInputSerializer(serializers.Serializer):
    nickname = serializers.CharField(max_length=25)
    role = serializers.ChoiceField(choices=[("observer", "observer"), ("voter", "voter")])
