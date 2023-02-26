from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


USERS_ROLE = (
    ('user', 'Пользователь'),
    ('admin', 'Администратор')
)


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
    role = models.CharField(max_length=15, choices=USERS_ROLE,
                            default='user', blank=True)
    REQUIRED_FIELDS = ('first_name', 'last_name', 'username')
    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.username

    @ property
    def is_user(self):
        return self.role == USERS_ROLE[0][0]

    @ property
    def is_admin(self):
        return self.is_superuser or self.role == USERS_ROLE[1][0]


class Subscribe(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                               related_name='subscribers')
    subscriber = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                                   related_name='authors')
