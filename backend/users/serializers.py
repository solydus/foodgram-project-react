from djoser.serializers import UserSerializer
from rest_framework import serializers

from .models import CustomUser, Follow
from recipes.models import Recipe
from recipes.utils import Base64ImageField


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj.id).exists()


class FollowRecipeImageSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )
        read_only_fields = fields


class FollowSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta(CustomUserSerializer.Meta):
        fields = [*CustomUserSerializer.Meta.fields,
                  'recipes', 'recipes_count']
        read_only_fields = ['__all__']

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj.id).exists()

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        recipes = obj.recipes.all()[:3]
        request = self.context.get('request')
        return FollowRecipeImageSerializer(
            recipes, many=True,
            context={'request': request}
        ).data
