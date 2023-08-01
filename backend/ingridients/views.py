from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Ingredient
from .serializers import IngredientSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    search_fields = ('^name',)
    pagination_class = None
