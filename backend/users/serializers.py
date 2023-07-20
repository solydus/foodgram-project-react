from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscribe, User
from .validators import (validate_cooking_time, validate_ingredients,
                         validate_tags)

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