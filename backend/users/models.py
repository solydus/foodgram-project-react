from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models
from django.db.models.functions import Length

models.CharField.register_lookup(Length)


class CustomUser(AbstractUser):
    first_name = models.CharField(
        'Имя',
        max_length=settings.CONST_LENGTH
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=settings.CONST_LENGTH
    )
    email = models.EmailField(
        'Email',
        unique=True,
        max_length=settings.CONST_LENGTH
    )
    username = models.CharField(
        'Логин',
        max_length=settings.CONST_LENGTH,
        unique=True,
        validators=[
            validators.MinLengthValidator(
                3,
                message='Логин должен быть длиннее 2х символов'
            )
        ]
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=('username', 'email'),
                name='unique_user'
            ),
            models.CheckConstraint(
                check=models.Q(username__length__gte=3),
                name="\nИмя должно быть длиннее\n",
            ),
        ]

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        CustomUser,
        related_name='followers',
        verbose_name='Подписчик',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        CustomUser,
        related_name='followings',
        verbose_name='Автор',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_follower'
            ),
            models.CheckConstraint(
                check=~models.Q(
                    author=models.F("user")),
                name="\nНельзя подписаться на себя\n"
            ),
        ]

    def __str__(self):
        return f'Автор: {self.author}, подписчик: {self.user}'
