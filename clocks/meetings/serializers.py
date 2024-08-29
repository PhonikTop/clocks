from rest_framework import serializers

from .models import Meeting


class MeetingSerializer(serializers.ModelSerializer):
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
