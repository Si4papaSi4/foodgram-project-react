from rest_framework import permissions


class IsAdminIsAuthorReadOnly(permissions.BasePermission):
    """
    Разрешает анонимному пользователю только безопасные запросы.
    Доступ к запросам PATCH и DELETE предоставляется только
    аутентифицированным пользователям с ролью admin или moderator,
    а также автору объекта.
    """

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
                and (request.user.is_superuser
                     or request.user == obj.author))
