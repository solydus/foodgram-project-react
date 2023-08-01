from django.contrib.auth.models import AbstractUser
from django.db import models

from .const import SYMBOLS_150, SYMBOLS_254, SYMBOLS_MESSAGE
from .mixins import validate_username


class User(AbstractUser):
    """Модель пользователя"""

    email = models.EmailField(
        'Адрес электронной почты',
        max_length=SYMBOLS_254,
        help_text=f'{SYMBOLS_MESSAGE} {SYMBOLS_254}.',
        unique=True
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=SYMBOLS_150,
        help_text=f'{SYMBOLS_MESSAGE} {SYMBOLS_150}.',
        unique=True,
        validators=(
            validate_username,
        )
    )
    first_name = models.CharField(
        'Имя',
        max_length=SYMBOLS_150,
        help_text=f'{SYMBOLS_MESSAGE} {SYMBOLS_150}.'
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=SYMBOLS_150,
        help_text=f'{SYMBOLS_MESSAGE} {SYMBOLS_150}.'
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username
