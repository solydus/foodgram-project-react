from colorfield.fields import ColorField
from django.db import models
from django.db.models import F, Q

from users.const import HEX, SYMBOLS_200
from users.models import User

from .validators import validate_amount, validate_cooking_time


class Tag(models.Model):
    name = models.CharField(
        max_length=SYMBOLS_200,
        unique=True,
        verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=SYMBOLS_200,
        unique=True,
        verbose_name='slug')
    color = ColorField(
        max_length=HEX,
        unique=True,
        verbose_name='Цвет'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=SYMBOLS_200,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=SYMBOLS_200,
        verbose_name='Единицы измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit'
            )
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=SYMBOLS_200,
        verbose_name='Название'
    )
    image = models.ImageField(
        upload_to='recipes',
        verbose_name='Картинка'
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        related_name='recipes',
        verbose_name='Ингредиент'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тег'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=(validate_cooking_time,),
        verbose_name='Время приготовления'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follow',
        verbose_name='Автор')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('author',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_follow'
            ),
            models.CheckConstraint(
                check=~Q(user=F('author')),
                name='self_following',
            ),
        ]

    def __str__(self):
        return f'{self.user} {self.author}'


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_amounts',
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_amounts',
        verbose_name='Рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        validators=(validate_amount,),
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient')]

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'


class BaseClassForFavoriteAndShopping(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True
        ordering = ('user',)

    def __str__(self):
        return f'{self.user} {self.recipe}'


class Favorite(BaseClassForFavoriteAndShopping):

    class Meta(BaseClassForFavoriteAndShopping.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        default_related_name = 'favorites'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite'
            )
        ]


class ShoppingList(BaseClassForFavoriteAndShopping):

    class Meta(BaseClassForFavoriteAndShopping.Meta):
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        default_related_name = 'shopping_list'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shoppingList'
            )
        ]
