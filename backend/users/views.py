from api.serializers import SubscriptionSerializer
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import Subscribe, User


class SubscribeCreateView(APIView):
    """
    API для обработки запросов, связанных с
    операциями CRUD (создание, чтение, обновление,
    удаление) для модели подписок.
    Два метода: post и delete, которые соответствуют
    операциям создания и удаления подписки соответственно.
    """
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
        serializer = SubscriptionSerializer(
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
