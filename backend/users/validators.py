from django.core.exceptions import ValidationError


def validate_username(value):
    if value == "me":
        raise ValidationError(
            "Имя пользователя 'me' зарезервировано системой."
        )
    if len(value) < 2:
        raise ValidationError(
            "Имя пользователя не может быть короче 2 символов."
        )
    return value
