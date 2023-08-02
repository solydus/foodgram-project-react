from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from recipes.models import Favorite, Recipe, ShoppingCart


class RecipeFilter(FilterSet):
    """
    Фильтрует рецепты по отношению к тегам, автору,
    избранному и нахождению в корзине пользователя.
    """
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(method='favorite_filter')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def filter_queryset_by_model(self, queryset, model, value):
        obj_pk = model.objects.filter(cart_owner=self.request.user).values('recipe_id')
        if value:
            return queryset.filter(pk__in=obj_pk)
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        return self.filter_queryset_by_model(queryset, Favorite, value)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        return self.filter_queryset_by_model(queryset, ShoppingCart, value)


class SearchFilterIngr(SearchFilter):
    search_param = 'name'
