from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter

from recipes.models import Favorite, Recipe, ShoppingCart


class RecipesFilter(filters.FilterSet):
    """
    фильтрация по избранному, автору, списку покупок и тегам.
    """
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated:
            rec_pk = Favorite.objects.filter(
                recipe_lover=self.request.user).values('recipe_id')
            if value:
                return queryset.filter(pk__in=rec_pk)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated:
            rec_pk = ShoppingCart.objects.filter(
                cart_owner=self.request.user).values('recipe_id')
            if value:
                return queryset.filter(pk__in=rec_pk)
        return queryset


class SearchFilterIngr(SearchFilter):
    """
    Кастомный фильтр для поиска по ингредиентам.
    """
    search_param = 'ingredient_name'
