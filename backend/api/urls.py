from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (RecipeViewSet,
                       TagViewSet,
                       UserViewSet,
                       IngredientViewSet)

app_name = 'api'
router = DefaultRouter()


router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('users', UserViewSet, basename='users')
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
    path(r'auth/', include('djoser.urls.authtoken')),
]
