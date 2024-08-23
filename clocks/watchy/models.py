from django.db import models
from django.contrib.auth.models import AbstractUser


class Room(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    current_session = models.OneToOneField(
        'Session',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='current_room'  # Задаем уникальное имя для обратной связи
    )

    def __str__(self):
        return self.name


class User(AbstractUser):
    nickname = models.CharField(max_length=100, default='Игрок')
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='users'  # Уникальное имя для обратной связи
    )
    is_observer = models.BooleanField(default=False)
    state = models.CharField(max_length=20, choices=[
        ('waiting', 'Waiting'),
        ('voting', 'Voting'),
        ('voted', 'Voted'),
    ], default='waiting')

    def __str__(self):
        return self.nickname


class Session(models.Model):
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='sessions'  # Уникальное имя для обратной связи
    )
    task_name = models.CharField(max_length=200)
    votes = models.JSONField(default=dict)
    average_score = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('completed', 'Completed'),
    ], default='active')

    def __str__(self):
        return f"Session for {self.room.name} - {self.task_name}"
