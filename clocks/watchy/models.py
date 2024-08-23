from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class Room(models.Model):
    name: str = models.CharField(max_length=100)
    is_active: bool = models.BooleanField(default=True)
    current_session: "Session" = models.OneToOneField(
        "Session",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="current_room",  # Задаем уникальное имя для обратной связи
    )

    def __str__(self) -> str:
        return self.name


class UserManager(BaseUserManager):
    def create_user(self, nickname: str, password: str | None = None, **extra_fields) -> "User":
        """
        Создание и сохранение обычного пользователя с заданным никнеймом и паролем.
        """
        if not nickname:
            msg = "The nickname field must be set"
            raise ValueError(msg)
        user = self.model(nickname=nickname, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, nickname: str, password: str | None = None, **extra_fields) -> "User":
        """
        Создание и сохранение суперпользователя с заданным никнеймом и паролем.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(nickname, password, **extra_fields)


class User(AbstractBaseUser):
    nickname: str = models.CharField(max_length=100, unique=True, default="Игрок")
    room: Room = models.ForeignKey("Room", on_delete=models.CASCADE, related_name="users")
    is_observer: bool = models.BooleanField(default=False)
    state: str = models.CharField(
        max_length=20,
        choices=[
            ("waiting", "Waiting"),
            ("voting", "Voting"),
            ("voted", "Voted"),
        ],
        default="waiting",
    )

    # Required fields for AbstractBaseUser
    USERNAME_FIELD: str = "nickname"
    REQUIRED_FIELDS: list[str] = []

    objects: UserManager = UserManager()

    def __str__(self) -> str:
        return self.nickname


class Session(models.Model):
    room: Room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="sessions",  # Уникальное имя для обратной связи
    )
    task_name: str = models.CharField(max_length=200)
    votes: dict = models.JSONField(default=dict)
    average_score: float = models.FloatField(null=True, blank=True)
    status: str = models.CharField(
        max_length=20,
        choices=[
            ("active", "Active"),
            ("completed", "Completed"),
        ],
        default="active",
    )

    def __str__(self) -> str:
        return f"Session for {self.room.name} - {self.task_name}"
