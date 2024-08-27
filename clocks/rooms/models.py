from django.db import models


# Create your models here.
class Room(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    current_session = models.OneToOneField(
        "meetings.Session",  # Используем строковую ссылку на модель Session
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="current_room",
    )

    def __str__(self) -> str:
        return self.name
