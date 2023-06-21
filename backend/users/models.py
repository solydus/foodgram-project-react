from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models

from .validators import validate_real_name, validate_username


class User(AbstractUser):
    username = models.CharField(
        verbose_name='Логин',
        max_length=settings.USER_MAX_LENGTH,
        unique=True,
        validators=[
            UnicodeUsernameValidator(),
            validate_username,
            MinLengthValidator(3),
            MaxLengthValidator(settings.USER_MAX_LENGTH)
        ]
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=settings.USER_MAX_LENGTH,
        validators=[validate_real_name],
        blank=False,
        null=False
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=settings.USER_MAX_LENGTH,
        validators=[validate_real_name],
        blank=False,
        null=False
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=settings.PASSWORD_MAX_LENGTH,
        null=True,
        blank=True
    )
    email = models.EmailField(
        verbose_name='Email',
        max_length=settings.EMAIL_MAX_LENGTH,
        unique=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Автор'
    )

    class Meta:
        ordering = ('-author_id',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author'
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F('user')),
                name='not_subscribe_yourself'
            )
        ]

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'
