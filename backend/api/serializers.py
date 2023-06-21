from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscribe, User
from .validators import (validate_cooking_time, validate_ingredients,
                         validate_tags)
from recipes.serializers import RecipeToRepresentationSerializer


class RecipeToRepresentationSerializer(serializers.ModelSerializer):
    """ отображения модели Recipe  """
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class TagSerializer(serializers.ModelSerializer):
    """ модель Tag. """
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """ модель Favorite. добавить/удалить список рецов """
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = serializers.CharField(source='recipe.image', read_only=True)
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')
    like_recipe = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
        write_only=True
    )

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time', 'like_recipe')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')

    def validate_like_recipe(self, value):
        user = self.context.get('request').user
        recipe = self.context.get('recipe')
        if Favorite.objects.filter(like_recipe=user, recipe=recipe).exists():
            raise serializers.ValidationError('Рецепт уже в избранном')
        return value

    def create(self, validated_data):
        recipe = self.context.get('recipe')
        user = validated_data.pop('like_recipe')
        favorite, created = Favorite.objects.get_or_create(recipe=recipe, like_recipe=user, defaults={})
        return favorite



class IngredientSerializer(serializers.ModelSerializer):
    """ Ingredient - просмотр списка или конкретного """
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class UserSerializer(serializers.ModelSerializer):
    """ работает с User, отображение рецептов в сериализаторе RecipeSerializer.
    """
    @property
    def is_subscribed(self):
        """ true/false на подписчика """
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.follower.filter(author=self.instance).exists()

    class Meta:
        model = User
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'is_subscribed')


class RecipeSerializer(serializers.ModelSerializer):
    """ сериализует рецепты """
    class Meta:
        model = Recipe
        fields = ('id', 'title', 'description',
                  'cooking_time', 'created_at')

class UserSerializer(serializers.ModelSerializer):
    """ сериализует пользователей """
    recipes = RecipeSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'recipes')

class SubscribeSerializer(serializers.ModelSerializer):
    """ вывели инфу про автора/рецы """
    author = UserSerializer(read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Subscribe
        fields = ('author', 'is_subscribed')

    def get_is_subscribed(self, obj):
        """ список подпис """
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.follower.filter(author=obj.author).exists()


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField(use_url=True, max_length=None)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author',
            'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name',
            'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            recipe=obj, like_recipe=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            recipe=obj, cart_owner=request.user).exists()

    def get_ingredients(self, obj):
        queryset = IngredientInRecipe.objects.filter(recipe=obj)
        return IngredientInRecipeSerializer(queryset, many=True).data

    def validate(self, data):
        tags = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')
        cooking_time = data.get('cooking_time')

        if not tags:
            raise serializers.ValidationError({
                'tags': 'Кажется вы забыли указать тэги'})
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'Кажется вы забыли указать ингредиенты'})
        validate_tags(tags, Tag)
        validate_ingredients(ingredients, Ingredient)
        validate_cooking_time(cooking_time)
        data.update({
            'tags': tags,
            'ingredients': ingredients,
            'author': self.context.get('request').user
        })
        return data

    def create(self, validated_data):
        tags = self.validated_data.pop('tags')
        ingredients = self.validated_data.pop('ingredients')
        new_recipe = Recipe.objects.create(
            name=self.validated_data.pop('name'),
            image=self.validated_data.pop('image'),
            text=self.validated_data.pop('text'),
            cooking_time=self.validated_data.pop('cooking_time'),
            author=self.validated_data.pop('author'))
        new_recipe.tags.add(*tags)
        bulk_create_data = (
            IngredientInRecipe(
                recipe=new_recipe,
                ingredient=get_object_or_404(
                    Ingredient, id=ingredient.get('id')),
                amount=ingredient.get('amount'))
            for ingredient in ingredients)
        IngredientInRecipe.objects.bulk_create(bulk_create_data)
        return new_recipe

    def update(self, instance, validated_data):
        new_tags = self.validated_data.pop('tags')
        new_ingredients = self.validated_data.pop('ingredients')

        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        instance.save()

        IngredientInRecipe.objects.filter(recipe=instance).delete()
        bulk_create_data = (
            IngredientInRecipe(
                recipe=instance,
                ingredient=get_object_or_404(
                    Ingredient, id=ingredient.get('id')),
                amount=ingredient.get('amount'))
            for ingredient in new_ingredients)
        IngredientInRecipe.objects.bulk_create(bulk_create_data)

        instance.tags.clear()
        instance.tags.set(new_tags)

        return instance
    

class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('cart_owner', 'recipe')
        read_only_fields = ('cart_owner', 'recipe')

    def validate(self, data):
        cart_owner = self.context.get('request').user
        recipe = self.context.get('recipe')
        data['recipe'] = recipe
        data['cart_owner'] = cart_owner
        if ShoppingCart.objects.filter(cart_owner=cart_owner, recipe=recipe).exists():
            raise serializers.ValidationError({'errors': 'The recipe is already in the shopping cart.'})
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeToRepresentationSerializer(instance.recipe, context={'request': request}).data