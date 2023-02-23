from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class CustomUser(AbstractUser):
    username = models.CharField(
        max_length=settings.MAX_LENGTH_CHARFIELD_CUSTOMUSER,
        unique=True, verbose_name='Логин'
    )
    email = models.EmailField(verbose_name='Электропочта',
                              unique=True)
    first_name = models.CharField(
        max_length=settings.MAX_LENGTH_CHARFIELD_CUSTOMUSER,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=settings.MAX_LENGTH_CHARFIELD_CUSTOMUSER,
        verbose_name='Фамилия'
    )
    password = models.CharField(
        max_length=settings.MAX_LENGTH_CHARFIELD_CUSTOMUSER
    )

    def __str__(self):
        return self.username
