from djoser.permissions import CurrentUserOrAdminOrReadOnly
from rest_framework import permissions


class IsAdminIsAuthorReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
                and (request.user.is_superuser
                     or request.user == obj.author))


class CustomCurrentUserOrAdminOrReadOnly(permissions.IsAuthenticatedOrReadOnly,
                                         CurrentUserOrAdminOrReadOnly):
    def has_permission(self, request, view):
        if not request.user.is_authenticated and view.action == 'me':
            return False
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        return super(
            CurrentUserOrAdminOrReadOnly,
            self
        ).has_object_permission(request, view, obj)
