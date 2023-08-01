from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from django.shortcuts import get_object_or_404

from .models import CustomUser, Follow
from .serializers import CustomUserSerializer, FollowSerializer


class UsersViewSet(DjoserUserViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.AllowAny]

    @action(methods=['GET'], detail=False,
            permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        user = self.request.user
        authors = CustomUser.objects.filter(followings__user=user)
        page = self.paginate_queryset(authors)
        serializer = FollowSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=['POST'], detail=True,
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, id):
        user = self.request.user
        author = get_object_or_404(CustomUser, id=id)
        subscription = Follow.objects.filter(user=user, author=author)
        if subscription.exists():
            return Response(
                {'error': 'Вы подписаны на этого автора'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = FollowSerializer(author, context={'request': request})
        Follow.objects.create(user=user, author=author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id):
        user = self.request.user
        author = get_object_or_404(CustomUser, id=id)
        subscription = Follow.objects.filter(user=user, author=author)
        if not subscription.exists():
            return Response(
                {'error': 'Вы не подписаны на этого автора'},
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
