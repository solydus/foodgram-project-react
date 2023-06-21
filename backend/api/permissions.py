from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """ только автор может изменять объекты.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user.is_authenticated
            and request.user.is_active
            and request.user == obj.author
        )
