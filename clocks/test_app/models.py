from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    cookie_key = models.TextField()

    def __str__(self):
        return self.username
