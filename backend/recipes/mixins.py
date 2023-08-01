from rest_framework import mixins, viewsets
from rest_framework.response import Response


class PatchModelMixin:
    def partial_update(self, request, *args, **kwargs):
        partial = True
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class CreateRetrievListPatchDestroyViewSet(mixins.CreateModelMixin,
                                           mixins.RetrieveModelMixin,
                                           PatchModelMixin,
                                           mixins.DestroyModelMixin,
                                           mixins.ListModelMixin,
                                           viewsets.GenericViewSet):
    pass
