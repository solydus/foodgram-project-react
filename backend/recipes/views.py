from fpdf import FPDF
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from backend.api.paginations import LimitPagination
from backend.api.permissions import AuthorStaffOrReadOnly
from .filters import RecipeFilter
from .mixins import CreateRetrievListPatchDestroyViewSet
from .models import IngredientsAmount, Recipe
from .serializers import (FavoriteRecipeSerializer,
                          RecipeCreateUpdateSerializer, RecipeListSerializer,
                          ShoppingCartSerializer,)


class RecipeViewSet(CreateRetrievListPatchDestroyViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = [AuthorStaffOrReadOnly]
    pagination_class = LimitPagination

    def get_serializer_class(self):
        if self.action in permissions.SAFE_METHODS:
            return RecipeListSerializer
        return RecipeCreateUpdateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def action_post(self, pk, serializer_class):
        user = self.request.user

        serializer = serializer_class(
            data={'user': user.id, 'recipe': pk},
            context={'request': self.request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def action_delete(self, pk, serializer_class):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        model_obj = serializer_class.Meta.model.objects.filter(
            user=user, recipe=recipe
        )
        if self.request.method == 'DELETE':
            if not model_obj.exists():
                return Response({'error': 'Рецепта нет в избранном.'},
                                status=status.HTTP_400_BAD_REQUEST)
        model_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['POST'], detail=True,
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        return self.action_post(pk, FavoriteRecipeSerializer)

    @favorite.mapping.delete
    def favorite_delete(self, request, pk=None):
        return self.action_delete(pk, FavoriteRecipeSerializer)

    @action(methods=['POST'], detail=True,
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        return self.action_post(pk, ShoppingCartSerializer)

    @shopping_cart.mapping.delete
    def shopping_cart_delete(self, request, pk=None):
        return self.action_delete(pk, ShoppingCartSerializer)

    @action(methods=['GET'], detail=False,
            permission_classes=[permissions.IsAuthenticated],
            pagination_class=None)
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = IngredientsAmount.objects.filter(
            recipe__shopcarts__user=user).values(
                'ingredient__name', 'ingredient__measurement_unit').annotate(
                    Sum('amount', distinct=True))
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font(
            'Teddy', '', './recipes/fonts/teddy-bear.ttf', uni=True)
        pdf.set_font('Teddy', size=14)
        pdf.cell(txt='Список покупок', center=True)
        pdf.ln(8)
        for i, ingredient in enumerate(ingredients):
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['amount__sum']
            pdf.cell(40, 10, f'{i + 1}) {name} - {amount} {unit}')
            pdf.ln()
        file = pdf.output(dest='S')
        response = HttpResponse(
            content_type='application/pdf', status=status.HTTP_200_OK)
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.pdf"')
        response.write(bytes(file))
        return response
