from rest_framework import mixins, viewsets


class CreateDestroyAll(mixins.CreateModelMixin,
                       mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):
    """ Вьюсет определяющий методы POST и DELETE """
    pass
