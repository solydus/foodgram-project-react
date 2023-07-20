import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User


def validate_real_name(value):
    """
    Валидатор для проверки корректности реального имени пользователя.
    """
    if not re.match(r'^[a-zA-Zа-яА-ЯёЁ\s]+$', value):
        raise ValidationError(_('Введите корректное имя.'))
    if value.lower() == 'me':
        raise ValidationError({
            f'Username не может быть {value}'})


def validate_username(value):
    """
    Валидатор для проверки корректности имени пользователя.
    """
    if not re.match(r'^[\w.@+-]+$', value):
        raise ValidationError(_('Имя пользователя может содержать только буквы, цифры и символы @/./+/-/_.'))

def validate_email(value):
    if User.objects.filter(email=value).exists():
        raise ValidationError(_('Данный адрес электронной почты уже занят.'))

def validate_username(value):
    if User.objects.filter(username=value).exists():
        raise ValidationError(_('Данное имя пользователя уже занято.'))
