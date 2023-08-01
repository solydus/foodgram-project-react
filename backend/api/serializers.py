from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import Subscription

User = get_user_model()


class UserSerializer(UserSerializer):
    """Сериализатор отображения пользователя."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_subscribed",
        )

    def get_is_subscribed(self, other_user):
        user = self.context["request"].user
        if user.is_anonymous or other_user == user:
            return False
        return Subscription.objects.filter(
            subscriber=user, author=other_user
        ).exists()


class UserCreateSerializer(UserCreateSerializer):
    """Сериализатор создания пользователя."""

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = "__all__"


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели, связывающей ингредиенты и рецепт."""

    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = RecipeIngredient
        fields = ["id", "name", "amount", "measurement_unit"]


class RecipeGetSerializer(serializers.ModelSerializer):
    """Сериализатор вывода рецептов."""

    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField()
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "text",
            "author",
            "cooking_time",
            "tags",
            "image",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
        )

    def get_ingredients(self, recipe):
        """Возвращает список ингредиентов рецепта."""

        return recipe.ingredients.values(
            "id",
            "name",
            "measurement_unit",
            amount=F("recipeingredient__amount"),
        )

    def get_is_favorited(self, recipe):
        """Проверяет, добавлен ли рецепт в избранное текущего пользователя."""
        user = self.context["request"].user
        if user.is_anonymous:
            return False
        return user.favorite_recipes.filter(recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        """Проверяет, добавлен ли рецепт /
        в список покупок текущего пользователя."""
        user = self.context["request"].user
        if user.is_anonymous:
            return False
        return user.shopping_list.filter(recipe=recipe).exists()


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор вывода ингредиентов (без количества)."""

    class Meta:
        model = Ingredient
        fields = "__all__"


class AddIngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор добавления ингредиента в рецепт."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ["id", "amount"]


@transaction.atomic
class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания и обновления рецепта."""

    ingredients = AddIngredientRecipeSerializer(
        many=True,
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        error_messages={"does_not_exist": "Указанного тега нет в базе данных"},
    )
    image = Base64ImageField()
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def validate_tags(self, tags):
        for tag in tags:
            if not Tag.objects.filter(id=tag.id).exists():
                raise serializers.ValidationError(
                    "Указанного тега нет в базе данных"
                )
        return tags

    def validate_ingredients(self, ingredients_to_validate):
        validated_ingredients = []
        if not ingredients_to_validate:
            raise serializers.ValidationError(
                "В рецепте должен быть как минимум 1 ингредиент."
            )
        for ing in ingredients_to_validate:
            if ing in validated_ingredients:
                raise serializers.ValidationError("Такой ингредиент уже есть")
            validated_ingredients.append(ing)
            if int(ing.get("amount")) < 1:
                raise serializers.ValidationError(
                    "Неверно указано количество ингредиента"
                )
        return validated_ingredients

    def create_ingredients(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    ingredient_id=ing["id"],
                    recipe=recipe,
                    amount=ing["amount"],
                )
                for ing in ingredients
            ]
        )

    def create(self, validated_data):
        author = self.context["request"].user
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        RecipeIngredient.objects.filter(recipe=instance).delete()
        instance.tags.set(validated_data.pop("tags"))
        ingredients = validated_data.pop("ingredients")
        self.create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeGetSerializer(
            instance, context={"request": self.context.get("request")}
        ).data


class BriefRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор вывода рецепта с сокращенным набором полей /
    (для подписок, избранного и списка покупок)."""

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор подписок."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def validate(self, data):
        """Проверяет правильность данных перед подпиской на автора."""
        author_id = (
            self.context.get("request").parser_context.get("kwargs").get("id")
        )
        author = get_object_or_404(User, id=author_id)
        user = self.context["request"].user
        if author.subscribers.filter(id=user.id).exists():
            raise serializers.ValidationError(
                detail=f"Пользователь{user} уже подписан на автора {author}",
            )
        if user == author:
            raise serializers.ValidationError(
                detail="Пользователь не может подписаться на самого себя",
            )
        return data

    def get_is_subscribed(self, other_user):
        user = self.context["request"].user
        if user.is_anonymous or other_user == user:
            return False
        return Subscription.objects.filter(
            subscriber=user, author=other_user
        ).exists()

    def get_recipes(self, author):
        """Возвращает рецепты автора в подписках пользователя."""
        limit = self.context.get("request").GET.get("recipes_limit")
        recipes = author.recipes.all()
        if limit:
            recipes = recipes[: int(limit)]
        serializer = BriefRecipeSerializer(recipes, many=True, read_only=True)
        return serializer.data

    def get_recipes_count(self, author):
        """Возвращает общее количество рецептов автора /
        в подписках пользователя."""
        return author.recipes.count()
