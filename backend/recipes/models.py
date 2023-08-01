from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    """Модель ингредиента"""

    name = models.CharField(
        max_length=60,
        verbose_name="Название ингредиента",
        unique=True,
        db_index=True,
    )
    measurement_unit = models.CharField(
        max_length=60,
        verbose_name="Единица измерения",
    )

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}"

    class Meta:
        ordering = ("name",)
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "measurement_unit"],
                name="unique_name_measurement_unit",
            )
        ]


class Tag(models.Model):
    """Модель тега"""

    name = models.CharField(
        max_length=60,
        verbose_name="Название",
        db_index=True,
    )
    color = models.CharField(
        max_length=7,
        verbose_name="Цветовой код (hex)",
        unique=True,
    )
    slug = models.SlugField(
        max_length=60,
        verbose_name="URL-путь к данному тэгу",
        unique=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"


class Recipe(models.Model):
    """Модель рецепта"""

    name = models.CharField(
        max_length=150,
        verbose_name="Название рецепта",
        help_text="Добавьте название рецепта",
        db_index=True,
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор рецепта",
        help_text="Выберите автора рецепта из списка",
    )

    image = models.ImageField(
        upload_to="recipes/images/",
        verbose_name="Изображение",
        help_text="Добавьте фото к рецепту",
    )

    text = models.TextField(
        verbose_name="Описание рецепта",
        help_text="Добавьте подробное описание рецепта",
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        related_name="recipes",
        through="RecipeIngredient",
        verbose_name="Ингредиенты",
    )

    tags = models.ManyToManyField(
        Tag,
        related_name="recipes",
        through="RecipeTag",
        verbose_name="Теги",
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления (в минутах)",
        validators=[MinValueValidator(1)],
    )

    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Время публикации"
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"


class RecipeIngredient(models.Model):
    """Модель связи рецептов и ингредиентов"""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
    )
    amount = models.IntegerField(
        verbose_name="Количество", validators=[MinValueValidator(1)]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="unique_recipe_ingredient",
            )
        ]


class RecipeTag(models.Model):
    """Модель связи рецептов и тегов"""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name="Тег",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "tag"],
                name="unique_recipe_tag",
            )
        ]


class Favorites(models.Model):
    """Модель связи пользователей и избранных рецептов"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorite_recipes",
        verbose_name="Пользователь, добавивший в избранное",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="added_to_favorites",
        verbose_name="Рецепт, добавленный в избранное",
    )

    def __str__(self):
        return f"Рецепт {self.recipe} в избранном пользователя {self.user}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_user_favorite_recipes",
            )
        ]
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"


class ShoppingList(models.Model):
    """Модель связи пользователей и списка покупок"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_list",
        verbose_name="Пользователь, добавивший в список покупок",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="added_to_shopping_list",
        verbose_name="Рецепт",
    )

    def __str__(self):
        return (
            f"Рецепт {self.recipe} в списке покупок пользователя {self.user}"
        )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_user_recipe_shopping_list",
            )
        ]
        verbose_name = "Список покупок"
        verbose_name_plural = "Список покупок"
