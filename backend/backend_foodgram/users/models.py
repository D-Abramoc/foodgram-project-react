from django.contrib.auth.models import AbstractUser
from django.db import models


MAX_LENGTH = 254


class CustomUser(AbstractUser):
    username = models.CharField(verbose_name='Логин',
                                max_length=MAX_LENGTH, unique=True,
                                blank=False)
    email = models.EmailField(verbose_name='Электропочта',
                              max_length=MAX_LENGTH, unique=True, blank=False)
    first_name = models.CharField(verbose_name='Имя',
                                  max_length=MAX_LENGTH, blank=False, null=False)
    last_name = models.CharField(verbose_name='Фамилия',
                                 max_length=MAX_LENGTH, blank=False, null=False)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
