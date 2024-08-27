from django.db import models


class Session(models.Model):
    room = models.ForeignKey(
        "rooms.Room",  # Используем строковую ссылку на модель Room
        on_delete=models.CASCADE,
        related_name="sessions",
    )
    task_name = models.CharField(max_length=200)
    votes = models.JSONField(default=dict)
    average_score = models.FloatField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("active", "Active"),
            ("completed", "Completed"),
        ],
        default="active",
    )

    def __str__(self) -> str:
        return f"Session for {self.room.name} - {self.task_name}"

