from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from recipes.models import Favorite, Recipe, ShoppingCart


class RecipeFilter(FilterSet):
    """
    Фильтрует рецепты по отношению к тегам, автору,
    избранному и нахождению в корзине пользователя.
    """
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def custom_filter(self, queryset, name, value, model):
        item_ids = model.objects.filter(
            cart_owner=self.request.user
        ).values_list('recipe_id', flat=True)

        if value:
            return queryset.filter(pk__in=item_ids)
        return queryset

    def favorite_filter(self, queryset, name, value):
        return self.custom_filter(queryset, name, value, Favorite)

    def shopping_cart_filter(self, queryset, name, value):
        return self.custom_filter(queryset, name, value, ShoppingCart)


class SearchFilterIngr(SearchFilter):
    """
    Кастомный фильтр для поиска по ингредиентам.
    """
    search_param = 'ingredient_name'
