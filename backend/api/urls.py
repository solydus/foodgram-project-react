from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    RecipeViewSet,
    FavoriteViewSet,
    SubscriptionsViewSet,
    TagViewSet,
    IngredientViewSet,
    ShoppingCartViewSet,
    DownloadShoppingCart,
    SubscribeAPIView,
)
import djoser.urls.authtoken
import djoser.urls

app_name = 'api'

router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')
router.register(
    r'recipes/(?P<recipe_id>\d+)/favorite',
    FavoriteViewSet, basename='favorite'
)
router.register(
    'users/subscriptions',
    SubscriptionsViewSet, basename='subscriptions'
)
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart',
    ShoppingCartViewSet, basename='shopping_cart'
)

urlpatterns = [
    path(
        'recipes/download_shopping_cart/',
        DownloadShoppingCart.as_view(),
        name='download_shopping_cart'
    ),
    path('', include(router.urls)),
    path('', include(djoser.urls)),
    path('auth/', include(djoser.urls.authtoken)),
    path('users/<int:author_id>/subscribe/', SubscribeAPIView.as_view(), name='subscribe'),
]
