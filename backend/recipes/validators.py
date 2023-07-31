from django.core.exceptions import ValidationError
from django.db import models


def validate_amount(value):
    if value <= 0:
        raise ValidationError(
            'Количество ингредиентов '
            'не может быть отрицательным или равняться 0.'
        )


def validate_cooking_time(value):
    if value < 1:
        raise ValidationError(
            'Минимальное время приготовления 1 минута.'
        )


def unique_constraint(name, *fields):
    return models.UniqueConstraint(
        fields=fields,
        name=name
    )
