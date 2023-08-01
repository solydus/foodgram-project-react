from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username


class User(AbstractUser):
    """Модель пользователя."""

    username = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="Имя пользователя",
        help_text="Введите имя пользователя",
        validators=[validate_username],
    )

    email = models.EmailField(
        max_length=60,
        unique=True,
        verbose_name="Электронная почта",
        help_text="Введите адрес электронной почты",
    )

    first_name = models.CharField(
        max_length=60,
        verbose_name="Имя",
        help_text="Укажите Ваше имя",
    )

    last_name = models.CharField(
        max_length=60,
        verbose_name="Фамилия",
        help_text="Укажите Вашу фамилию",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
        "first_name",
        "last_name",
    ]

    def __str__(self):
        return f"{self.username} ({self.first_name} {self.last_name})"

    class Meta:
        ordering = ("username",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Subscription(models.Model):
    """Модель подписок пользователя."""

    author = models.ForeignKey(
        User,
        related_name="subscriptions",
        on_delete=models.CASCADE,
        verbose_name="Автор рецептов",
    )
    subscriber = models.ForeignKey(
        User,
        related_name="subscribers",
        on_delete=models.CASCADE,
        verbose_name="Подписчик",
    )

    def __str__(self):
        return f"Автор {self.author} - подписчик {self.subscriber}"

    class Meta:
        ordering = ["-id"]
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=["author", "subscriber"],
                name="unique_subscription",
            ),
            models.CheckConstraint(
                check=~models.Q(subscriber=models.F("author")),
                name="user_subscribes_to_self",
            ),
        ]
