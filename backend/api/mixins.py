from rest_framework import mixins, viewsets


class CreateDestroyAll(mixins.CreateModelMixin,
                       mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):
    """ Для методов POST/DELETE """
    pass
