import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_hex(value):
    """
    Валидатор для проверки корректности шестнадцатеричного кода цвета.
    """
    if not re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', value):
        raise ValidationError(_('Цвет в формате #RRGGBB.'))


def validate_ingredient_name(value):
    """
    Валидатор для проверки корректности имени ингредиента.
    """
    if not re.match(r'^[a-zA-Z0-9,&()\. -]+$', value):
        raise ValidationError(_('Имя ингредиента содержать  буквы'))


class UnicodeUsernameValidator:
    """
    Валидатор для проверки допустимости символов в имени пользователя.
    """
    regex = r'^[\w.@+-]+$'
    message = _('Имя пользователя может содержать только буквы')

    def __call__(self, value):
        """
        Проверка значения на допустимость символов.
        """
        if not re.match(self.regex, value):
            raise ValidationError(self.message)
