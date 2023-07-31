import re

from django.core.exceptions import ValidationError

from .const import NOT_ALLOWED_CHAR_MSG, NOT_ALLOWED_ME, USERNAME_REGEX


def validate_username(username):
    invalid_symbols = ''.join(set(re.sub(USERNAME_REGEX, '', username)))
    if invalid_symbols:
        raise ValidationError(
            NOT_ALLOWED_CHAR_MSG.format(
                chars=invalid_symbols, username=username))
    if username == 'me':
        raise ValidationError(NOT_ALLOWED_ME.format(username=username))
    return username


class ValidateMixin:
    @staticmethod
    def validate_username(username):
        return validate_username(username)
