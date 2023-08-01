from django.conf import settings
from django.db import models


class Ingredient(models.Model):
    name = models.CharField(
        'Название',
        max_length=settings.CONST_LENGTH,
        db_index=True
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=50
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'
