import re

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_real_name(value):
    """
    Валидатор для проверки корректности реального имени пользователя.
    """
    if not re.match(r"^[a-zA-Za-яА-ЯёЁ\s]+$", value):
        raise ValidationError(_("Введите корректное имя."))
    if value.lower() == "me":
        raise ValidationError({f"Username не может быть {value}"})


def validate_username(value):
    """
    Валидатор для проверки корректности имени пользователя.
    """
    if not re.match(r"^[\w.@+-]+$", value):
        raise ValidationError(_("Имя может содержать только буквы, цифры"))

    if User.objects.filter(username=value).exists():
        raise ValidationError(_("Данное имя пользователя уже занято."))


def validate_email(value):
    if User.objects.filter(email=value).exists():
        raise ValidationError(_("Данный адрес электронной почты уже занят."))
