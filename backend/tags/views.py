from rest_framework import permissions
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Tag
from .serializers import TagSerializer


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = None
