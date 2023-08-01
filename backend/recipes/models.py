from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import validators
from django.db import models

from ingridients.models import Ingredient
from tags.models import Tag

User = get_user_model()


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор публикации'
    )
    name = models.CharField(
        'Название',
        max_length=settings.CONST_LENGTH,
        db_index=True
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recipe_images/%Y/%m/%d',
        default='static/images/DefaultCardImg.png'
    )
    text = models.TextField(
        'Текстовое описание',
        max_length=1000
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientsAmount',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        null=False,
        validators=[
            validators.MinValueValidator(
                1, message='Время не должно быть меньше 1'
            )
        ],
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name[:settings.NAME_PREVIEW]


class IngredientsAmount(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='amounts',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='amounts',
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            validators.MinValueValidator(
                1,
                message='Количество ингредиентов не должно быть меньше 1'
            )
        ],
        default=1,
        null=False,
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        return (
            f'{self.recipe.name}: {self.ingredient.name}'
            f'{self.amount}, {self.ingredient.measurement_unit}'
        )


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт')

    class Meta:
        verbose_name = 'Список избранного'
        verbose_name_plural = 'Список избранного'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_recipe'
            )
        ]

    def __str__(self):
        return f'{self.recipe} в избранном у {self.user}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopcarts'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепты',
        related_name='shopcarts'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart_recipe'
            )
        ]

    def __str__(self):
        return f'{self.recipe} в списке покупок у {self.user}'
