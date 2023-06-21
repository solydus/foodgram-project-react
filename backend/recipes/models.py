from django.conf import settings
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from api.validators import validate_hex, validate_ingredient_name
from users.models import User
from .models import Recipe, Ingredient


from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify

from validators import (UnicodeUsernameValidator, validate_hex,
                         validate_ingredient_name)


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Тэг',
        max_length=50,
        unique=True,
        validators=[UnicodeUsernameValidator()]
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=50,
        unique=True,
        blank=True,
        null=True
    )
    color = models.CharField(
        verbose_name='Цвет',
        max_length=7,
        default='#C71585',
        unique=True,
        validators=[validate_hex]
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=100,
        validators=[validate_ingredient_name]
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=50
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        'auth.User',
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        validators=[validate_ingredient_name]
    )
    image = models.ImageField(
        verbose_name='Фотография блюда',
        upload_to='recipes/images/',
        null=True,
        default=None
    )
    text = models.TextField(verbose_name='Описание')
    tags = models.ManyToManyField(Tag, verbose_name='Тэги')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (в минутах)',
        default=1,
        validators=[
            MinValueValidator(1, 'Должно быть больше 0'),
            MaxValueValidator(600, 'Превышен лимит времени приготовления')
        ]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'name'],
                name='unique_author_recipe_name'
            )
        ]

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='ingredients'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество в рецепте',
        validators=[
            MinValueValidator(1, 'Должно быть больше 0'),
            MaxValueValidator(2000, 'Максимальное количество - 2000')
        ]
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return f'{self.ingredient} ({self.amount})'


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    recipe_lover = models.ForeignKey(
        'auth.User',
        verbose_name='Добавил в избранное',
        on_delete=models.CASCADE,
        related_name='favorites'
    )

    class Meta:
        verbose_name = 'Любимый рецепт'
        verbose_name_plural = 'Любимые рецепты'

    def __str__(self):
        return f'{self.recipe} ({self.recipe_lover})'


class ShoppingCart(models.Model):
    cart_owner = models.ForeignKey(
        'auth.User',
        verbose_name='Владелец списка покупок',
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='shopping_carts'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'{self.recipe} ({self.cart_owner})'