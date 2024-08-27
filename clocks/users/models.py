from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


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
    from rooms.models import Room

    nickname: str = models.CharField(max_length=100, unique=True, default="Игрок")
    room: Room = models.ForeignKey("rooms.Room", on_delete=models.CASCADE, related_name="users")
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
