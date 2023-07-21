from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import (Favorite,
                            Ingredient,
                            Recipe,
                            ShoppingCart,
                            Tag)
from users.models import Subscribe, User

from .shopping_utils import generate_shopping_list
from .filters import SearchFilterIngr, RecipesFilter
from .mixins import CreateDestroyAll
from .paginators import PageNumPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (FavoriteRecipeSerializer,
                          IngredientSerializer,
                          RecipeSerializer,
                          ShoppingCartSerializer,
                          SubscribeSerializer,
                          TagSerializer)


class RecipeViewSet(
    mixins.ListModelMixin,  # Миксин для получения списка объектов
    mixins.CreateModelMixin,  # Миксин для создания нового объекта
    mixins.RetrieveModelMixin,  # Миксин для получения конкретного объекта
    mixins.UpdateModelMixin,  # Миксин для обновления объекта
    mixins.DestroyModelMixin,  # Миксин для удаления объекта
    viewsets.GenericViewSet  # Базовый класс для вьюсета
):
    queryset = Recipe.objects.all()  # Запрос для получения  объектов Recipe
    pagination_class = PageNumPagination  # Класс пагинации для списка объектов
    filter_backends = (DjangoFilterBackend,)  # Фильтр для применения фильтра
    filterset_class = RecipesFilter  # Класс фильтра для модели Recipe
    serializer_class = RecipeSerializer  # Сериализатор для модели Recipe
    permission_classes = [IsAuthorOrReadOnly]  # Классы разрешений к объектам


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    # Запрос, который будет использоваться для получения объектов Tag
    queryset = Tag.objects.all()
    # Сериализатор для преобразования объектов Tag в данные JSON
    serializer_class = TagSerializer


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    """ Добавление в список ингридиентов доступно только через админку """
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

    queryset = Subscribe.objects.none()  # Пустой queryset

    def get_queryset(self):
        return Subscribe.objects.filter(
            user=self.request.user).prefetch_related('author')


class SubscribeCreateView(APIView):
    """ сделать/удалить подписку """
    permission_classes = [IsAuthenticated, ]

    def post(self, request, author_id):
        author = get_object_or_404(User, id=author_id)
        if request.user == author:
            return Response(
                {'errors': 'Вы не можете подписаться на самого себя'},
                status=status.HTTP_400_BAD_REQUEST)
        subscription = Subscribe.objects.filter(
            author=author, user=request.user)
        if subscription.exists():
            return Response(
                {'errors': 'Вы уже подписаны на этого автора'},
                status=status.HTTP_400_BAD_REQUEST)
        queryset = Subscribe.objects.create(author=author, user=request.user)
        serializer = SubscribeSerializer(
            queryset, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, author_id):
        user = request.user
        author = get_object_or_404(User, id=author_id)
        subscription = Subscribe.objects.filter(
            author=author, user=user)
        if not subscription.exists():
            return Response(
                {'errors': 'Вы еще не подписаны на этого автора'},
                status=status.HTTP_400_BAD_REQUEST)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteRecipeSerializer
    permission_classes = [IsAuthenticated, ]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'recipe': self.kwargs.get('recipe_id')})
        return context

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('recipe_id'))
        serializer.save(
            recipe_lover=self.request.user, recipe=recipe)

    @action(methods=('delete',), detail=True)
    def delete(self, request, recipe_id):
        recipe = self.kwargs.get('recipe_id')
        recipe_lover = self.request.user
        if not Favorite.objects.filter(recipe=recipe,
                                       recipe_lover=recipe_lover).exists():
            return Response({'errors': 'Рецепт не в избранном'},
                            status=status.HTTP_400_BAD_REQUEST)
        get_object_or_404(
            Favorite,
            recipe_lover=recipe_lover,
            recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(CreateDestroyAll):
    """ Добавлять и удалять рецепты из корзины покупок """
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
    permission_classes = [IsAuthenticated, ]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('recipe_id'))
        context.update({'recipe': recipe})
        context.update({'cart_owner': self.request.user})
        return context

    @action(methods=('delete',), detail=True)
    def delete(self, request, recipe_id):
        recipe = self.kwargs.get('recipe_id')
        cart_owner = self.request.user
        if not ShoppingCart.objects.filter(recipe=recipe,
                                           cart_owner=cart_owner).exists():
            return Response({'errors': 'Рецепт не добавлен в список покупок'},
                            status=status.HTTP_400_BAD_REQUEST)
        get_object_or_404(
            ShoppingCart,
            cart_owner=cart_owner,
            recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DownloadShoppingCart(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        shopping_list = generate_shopping_list(request.user)
        if shopping_list is None:
            return Response({'errors': 'В вашем списке покупок ничего нет'},
                            status=status.HTTP_400_BAD_REQUEST)

        response = HttpResponse(shopping_list, content_type='text/plain')
        filename = 'shopping_list.txt'
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
