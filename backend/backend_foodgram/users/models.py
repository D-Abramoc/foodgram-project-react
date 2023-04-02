from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


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
    REQUIRED_FIELDS = ('first_name', 'last_name')
    USERNAME_FIELD = 'email'

    class Meta:
        ordering = ('username',)
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                               related_name='subscribers',
                               verbose_name='автор',
                               help_text='Выберите автора для подписки')
    subscriber = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='authors',
        verbose_name='подписчик',
        help_text='Выберите кто подписывается на автора'
    )

    class Meta:
        verbose_name = 'кто на кого подписан'
        verbose_name_plural = 'кто на кого подписан'
        constraints = [
            models.UniqueConstraint(fields=['author', 'subscriber'],
                                    name='unique_subscription'),
            models.CheckConstraint(
                check=~models.Q(subscriber=models.F('author')),
                name='prevent_self_subscribe'
            )
        ]

    def __str__(self):
        return (f'{self.subscriber.username} подписан '
                f'на {self.author.username}')
