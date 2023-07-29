from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ''' Модель пользователя '''

    email = models.EmailField(max_length=150, unique=True)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email


class Subscribe(models.Model):
    ''' Подписка на автора '''
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribing',
        verbose_name='Автор'
    )

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscribe'
            )
        ]
