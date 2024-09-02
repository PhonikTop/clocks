from rest_framework import serializers
from rooms.models import Room

from .models import Meeting


class MeetingSerializer(serializers.ModelSerializer):
    room = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all())
    task_name = serializers.CharField(max_length=100)
    votes = serializers.JSONField()
    average_score = serializers.FloatField(allow_null=True, required=False)
    active = serializers.BooleanField()

    class Meta:
        model = Meeting
        fields = ["id", "room", "task_name", "votes", "average_score", "active"]

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop("fields", None)
        super(MeetingSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
