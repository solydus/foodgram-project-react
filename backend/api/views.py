from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework import generics, mixins, status
from rest_framework.response import Response



from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscribe, User

from .filters import SearchFilterIngr, RecipesFilter
from .mixins import CreateDestroyAll
from .paginators import PageNumPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (FavoriteRecipeSerializer, IngredientSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          SubscribeSerializer, TagSerializer)


from rest_framework import mixins

class RecipeViewSet(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    queryset = Recipe.objects.all()
    pagination_class = PageNumPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthorOrReadOnly]


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (SearchFilterIngr,)
    search_fields = ('^name',)


class SubscriptionsViewSet(mixins.ListModelMixin,
                           mixins.CreateModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    serializer_class = SubscribeSerializer
    permission_classes = [IsAuthenticated, ]
    pagination_class = PageNumPagination

    def get_queryset(self):
        return Subscribe.objects.filter(
            user=self.request.user).prefetch_related('author')


from rest_framework.generics import CreateAPIView, DestroyAPIView

class SubscribeCreateView(CreateAPIView):
    serializer_class = SubscribeSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        author_id = self.kwargs.get('author_id')
        author = get_object_or_404(User, id=author_id)
        if self.request.user == author:
            raise serializers.ValidationError(
                {'errors': 'Вы не можете подписаться на самого себя'})
        subscription = Subscribe.objects.filter(
            author=author, user=self.request.user)
        if subscription.exists():
            raise serializers.ValidationError(
                {'errors': 'Вы уже подписаны на этого автора'})
        serializer.save(author=author, user=self.request.user)


class SubscribeDeleteView(DestroyAPIView):
    serializer_class = SubscribeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        author_id = self.kwargs.get('author_id')
        return get_object_or_404(Subscribe, author=author_id, user=self.request.user)


class FavoriteListView(generics.ListAPIView,
                       mixins.CreateModelMixin,
                       mixins.DestroyModelMixin):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteRecipeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        recipe_id = self.kwargs.get('recipe_id')
        return Favorite.objects.filter(recipe=recipe_id)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'recipe': self.kwargs.get('recipe_id')})
        return context

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('recipe_id'))
        serializer.save(like_recipe=self.request.user, recipe=recipe)

    @action(methods=('delete',), detail=True)
    def delete_favorite(self, request, pk=None, recipe_id=None):
        like_recipe = self.request.user
        try:
            favorite = Favorite.objects.get(pk=pk, recipe=recipe_id, like_recipe=like_recipe)
        except Favorite.DoesNotExist:
            return Response({'errors': 'Рецепт не в избранном'},
                            status=status.HTTP_400_BAD_REQUEST)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartListCreateView(generics.ListCreateAPIView):
    serializer_class = ShoppingCartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ShoppingCart.objects.filter(cart_owner=self.request.user)

    def perform_create(self, serializer):
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        serializer.save(cart_owner=self.request.user, recipe=recipe)


class ShoppingCartDeleteView(generics.DestroyAPIView):
    serializer_class = ShoppingCartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        recipe_id = self.kwargs.get('recipe_id')
        return get_object_or_404(
            ShoppingCart,
            cart_owner=self.request.user,
            recipe_id=recipe_id)

    def perform_destroy(self, instance):
        instance.delete()


class DownloadShoppingCartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = ShoppingCart.objects.filter(cart_owner=request.user)
        if not queryset.exists():
            return Response({'errors': 'В вашем списке покупок ничего нет'},
                            status=status.HTTP_400_BAD_REQUEST)

        ingredients = IngredientInRecipe.objects.filter(
            recipe_id__in=queryset.values('recipe_id')
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(
            amount=Sum('amount')
        ).order_by()

        text = 'Список покупок:\n\n'
        for item in ingredients:
            text += f'{item["ingredient__name"]}: {item["amount"]} {item["ingredient__measurement_unit"]}\n'

        response = HttpResponse(text, content_type='text/plain')
        filename = 'shopping_list.txt'
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
