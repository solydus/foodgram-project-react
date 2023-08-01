from ingridients.models import Ingredient
from rest_framework import exceptions, serializers

from backend.api.utils import Base64ImageField
from recipes.models import (FavoriteRecipe, IngredientsAmount, Recipe,
                            ShoppingCart,)
from tags.models import Tag
from tags.serializers import TagSerializer
from users.serializers import CustomUserSerializer


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ['__all__']


class IngredientsAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientsAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = serializers.SerializerMethodField(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_ingredients(self, obj):
        queryset = IngredientsAmount.objects.filter(recipe=obj)
        return IngredientsAmountSerializer(queryset, many=True).data

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.favorites.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.shopcarts.filter(user=user).exists()


class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientsAmount
        fields = ('id', 'amount')


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    ingredients = AddIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'ingredients', 'tags',
                  'image', 'name', 'text', 'cooking_time')

    def validate_tags(self, tags):
        if not tags:
            raise exceptions.ValidationError('Выберите тэг.')
        tag_list = []
        for tag in tags:
            if tag in tag_list:
                exceptions.ValidationError('Тэги должны быть уникальными.')
            tag_list.append(tag)

        return tags

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise exceptions.ValidationError(
                'Количество ингредиента не должно быть меньше 1'
            )

        ingredients_id_list = [ingredient['id'] for ingredient in ingredients]
        for ingredient_id in ingredients_id_list:
            if ingredients_id_list.count(ingredient_id) > 1:
                raise exceptions.ValidationError(
                    'Ингредиенты должны быть уникальными.'
                )
        return ingredients

    def validate_cooking_time(self, cooking_time):
        if cooking_time <= 0:
            raise exceptions.ValidationError(
                'Минимальное время приготовления 1 минута.'
            )
        return cooking_time

    @staticmethod
    def create_ingredients(ingredients, recipe):
        ingredients = [
            IngredientsAmount(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ]
        IngredientsAmount.objects.bulk_create(ingredients)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, recipe, validated_data):
        tags = validated_data.get('tags')
        ingredients = validated_data.get('ingredients')

        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)

        if ingredients:
            recipe.ingredients.clear()
            self.create_ingredients(ingredients, recipe)

        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeListSerializer(instance, context=context).data


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteRecipe
        fields = ('user', 'recipe')

    def validate(self, data):
        user, recipe = data.get('user'), data.get('recipe')
        if self.Meta.model.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                {'error': 'Рецепт уже добавлен.'}
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSerializer(instance.recipe, context=context).data


class ShoppingCartSerializer(FavoriteRecipeSerializer):
    class Meta(FavoriteRecipeSerializer.Meta):
        model = ShoppingCart
