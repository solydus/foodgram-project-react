from rest_framework import serializers
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """работает с User, отображение рецептов в RecipeSerializer."""

    is_subscribed = serializers.SerializerMethodField()

    @property
    def is_subscribed(self):
        """true/false на подписчика"""
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return user.follower.filter(author=self.instance).exists()

    class Meta:
        model = User
        fields = ("email", "id", "username",
                  "first_name", "last_name", "is_subscribed")
