from django.apps import AppConfig
from django.core.signals import setting_changed


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = 'Пользователи'

    def ready(self):
        from .signals import create_profile
        setting_changed.connect(create_profile)
