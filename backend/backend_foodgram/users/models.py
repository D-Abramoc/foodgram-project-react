from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class CustomUser(AbstractUser):
    username = models.CharField(max_length=settings.MAX_LENGTH_CHARFIELD,
                                unique=True)
    email = models.EmailField()
    first_name = models.CharField(max_length=settings.MAX_LENGTH_CHARFIELD)
    last_name = models.CharField(max_length=settings.MAX_LENGTH_CHARFIELD)

    def __str__(self):
        return self.username
