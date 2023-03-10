from django.core.exceptions import ValidationError


def validate_cooking_time(value):
    if value < 1:
        raise ValidationError(
            'Время готовки не может быть менее 1 минуты'
        )
    return value
