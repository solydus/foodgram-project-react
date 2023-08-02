from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import (Favorite, Ingredient, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscribe, User

from .shopping_utils import generate_shopping_list
from .filters import IngredientSearchFilter, RecipeFilter
from .mixins import CreateDestroyViewSet
from .paginators import PageLimitPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (FavoriteRecipeSerializer, IngredientSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          SubscriptionSerializer, TagSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    """
    viewset для работы с моделью Recipe.
    Он наследуется от ModelViewSet,
    что предоставляет все стандартные операции CRUD
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    pagination_class = PageLimitPagination


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    viewset для работы с моделью Tag.
    Он наследуется от ReadOnlyModelViewSet,
    предоставляет только операции чтения для модели Tag.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    viewset для работы с моделью Ingredient.
    Он также наследуется от ReadOnlyModelViewSet,
    поэтому предоставляет только операции чтения для модели Ingredient.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [IngredientSearchFilter]
    search_fields = ['^name']
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    используется для создания представления API,
    которое обеспечивает только чтение (read-only)
    операций для модели Ingredient
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class SubscriptionsViewSet(viewsets.ModelViewSet):
    """
    используется для обработки запросов,
    связанных с операциями CRUD (создание,
    чтение, обновление, удаление) для модели подписок.
    """
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated, ]
    pagination_class = PageLimitPagination

    def get_queryset(self):
        return Subscribe.objects.filter(
            user=self.request.user).prefetch_related('author')


class SubscribeCreateView(APIView):
    """
    API для обработки запросов, связанных с
    операциями CRUD (создание, чтение, обновление,
    удаление) для модели подписок.
    Два метода: post и delete, которые соответствуют
    операциям создания и удаления подписки соответственно.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, author_id):
        author = get_object_or_404(User, id=author_id)
        if request.user == author:
            return Response({
                'errors': 'Вы не можете подписаться на самого себя'},
                status=status.HTTP_400_BAD_REQUEST)

        subscription, created = Subscribe.objects.get_or_create(
            author=author, user=request.user)

        if not created:
            return Response({'errors': 'Вы уже подписаны на этого автора'},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = SubscriptionSerializer(
            subscription, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, author_id):
        author = get_object_or_404(User, id=author_id)
        subscription = get_object_or_404(
            Subscribe, author=author, user=request.user)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(viewsets.ModelViewSet):
    """
    реализует представление API для операций CRUD
    (создание, чтение, обновление и удаление)
    модели Favorite, связанной с моделью Recipe
    """
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


class ShoppingCartViewSet(CreateDestroyViewSet):
    """
    Реализует представление API для добавления
    и удаления рецептов из корзины покупок
    """
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
    permission_classes = [IsAuthenticated, ]

    def get_serializer_context(self):
        """
        Метод передает в сериализатор необходимые ему для создания модели
        атрибуты cart_owner и recipe.
        """
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
    """
    скачивание списка покупок в виде текстового файла
    """
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
