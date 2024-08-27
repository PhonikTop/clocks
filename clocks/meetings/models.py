from django.db import models


class Session(models.Model):
    room = models.ForeignKey(
        "rooms.Room",
        on_delete=models.CASCADE,
        related_name="sessions",
    )
    task_name = models.CharField(max_length=200)
    votes = models.JSONField(default=dict)
    average_score = models.FloatField(null=True, blank=True)
    active: bool = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"Session for {self.room.name} - {self.task_name}"
