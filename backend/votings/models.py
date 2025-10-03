from django.db import models


class Voting(models.Model):
    room = models.ForeignKey(
        "rooms.Room",
        on_delete=models.CASCADE,
        related_name="votings",
    )
    task_name = models.CharField(max_length=200)
    votes = models.JSONField(default=dict)
    average_score = models.FloatField(null=True, blank=True)
    active: bool = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Voting for {self.room.name} - {self.task_name}"

    def reset_to_default(self):
        self.active = True
        self.votes = {}
        self.average_score = None
        self.save()
