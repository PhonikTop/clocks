from django.db import models


class Room(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    current_session = models.OneToOneField(
        "meetings.Session",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="current_room",
    )
    users = models.JSONField(default=list)

    def __str__(self) -> str:
        return self.name
