from ingridients.views import IngredientViewSet
from rest_framework.routers import DefaultRouter


from django.urls import include, path

from tags.views import TagViewSet
from recipes.views import RecipeViewSet
from users.views import UsersViewSet

router_v1 = DefaultRouter()
router_v1.register('users', UsersViewSet, 'users')
router_v1.register('tags', TagViewSet, 'tags')
router_v1.register('ingredients', IngredientViewSet, 'ingredients')
router_v1.register('recipes', RecipeViewSet, 'recipes')

urlpatterns = (
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
)
