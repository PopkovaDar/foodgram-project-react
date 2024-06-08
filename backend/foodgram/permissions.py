from rest_framework import permissions


class IsAuthorAdminOrReadOnly(permissions.BasePermission):
    """Доступно для чтения или только Автору."""

    def has_object_permission(self, request, view, obj):
        return (
            obj.author == request.user
            or request.method in permissions.SAFE_METHODS
        )
