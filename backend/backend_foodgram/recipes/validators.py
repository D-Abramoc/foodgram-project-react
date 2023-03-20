from django.core.exceptions import ValidationError


def validate_minimum(value):
    if value < 1:
        raise ValidationError(
            'Значение не может быть менее 1'
        )
    return value


def validate_string(value):
    try:
        value = int(value)
    except ValueError:
        return value
    raise ValidationError(
        'Текст не может состоять из одних цифр'
    )
