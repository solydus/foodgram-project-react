import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_real_name(value):
    """
    Валидатор для проверки корректности реального имени пользователя.
    """
    if not re.match(r'^[a-zA-Zа-яА-ЯёЁ\s]+$', value):
        raise ValidationError(_('Введите корректное имя.'))


def validate_username(value):
    """
    Валидатор для проверки корректности имени пользователя.
    """
    if not re.match(r'^[\w.@+-]+$', value):
        raise ValidationError(_('Имя пользователя может содержать только буквы, цифры и символы @/./+/-/_.'))

