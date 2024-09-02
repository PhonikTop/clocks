from meetings.models import Meeting
from rest_framework import serializers

from .models import Room


class RoomSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=50)
    is_active = serializers.BooleanField()
    users = serializers.JSONField()
    current_meeting_id = serializers.PrimaryKeyRelatedField(queryset=Meeting.objects.all())

    class Meta:
        model = Room
        fields = ["id", "name", "is_active", "users", "current_meeting_id"]

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop("fields", None)
        super(RoomSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
