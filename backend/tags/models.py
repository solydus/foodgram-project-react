from django.conf import settings
from django.core import validators
from django.db import models


class Tag(models.Model):
    name = models.CharField(
        'Название',
        max_length=settings.CONST_LENGTH,
        unique=True
    )
    color = models.CharField(
        'Цветовой HEX-код',
        max_length=7,
        unique=True,
        default='#',
        validators=[
            validators.RegexValidator(
                regex=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Введенное значение в формате HEX'
            )
        ]
    )
    slug = models.SlugField(
        'Slug',
        max_length=settings.CONST_LENGTH,
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'color', 'slug'],
                name='unique_tag'
            )
        ]

    def __str__(self):
        return self.name
