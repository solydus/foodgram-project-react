from django_filters import rest_framework as filters
from recipes.models import Favorite, Recipe, ShoppingCart
from rest_framework.filters import SearchFilter


class RecipesFilter(filters.FilterSet):
    """
    Фильтрует рецепты по отношению к тегам, автору,
    избранному и нахождению в корзине пользователя.
    """
    is_in_shopping_cart = filters.BooleanFilter(method='shopping_cart_filter')
    is_favorited = filters.BooleanFilter(method='favorite_filter')
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def favorite_filter(self, queryset, name, value):
        recipe_ids = Favorite.objects.filter(
            like_recipe=self.request.user
        ).values_list('recipe_id', flat=True)
        if value:
            return queryset.filter(pk__in=recipe_ids)
        else:
            return queryset

    def shopping_cart_filter(self, queryset, name, value):
        recipe_ids = ShoppingCart.objects.filter(
            cart_owner=self.request.user
        ).values_list('recipe_id', flat=True)
        if value:
            return queryset.filter(pk__in=recipe_ids)
        return queryset


class SearchFilterIngr(SearchFilter):
    """
    Кастомный фильтр для поиска по ингредиентам.
    """
    search_param = 'ingredient_name'
