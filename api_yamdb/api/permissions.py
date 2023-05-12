from rest_framework.permissions import SAFE_METHODS, BasePermission


class OwnerOrAdmins(BasePermission):
    """Права для работы с пользователями."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (
                request.user.is_admin
                or request.user.is_superuser)
        )

    def has_object_permission(self, request, view, obj):
        return (
            obj == request.user
            or request.user.is_admin
            or request.user.is_superuser)


class IsAdminOrReadOnly(BasePermission):
    """Права для работы с категориями и жанрами."""
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and (request.user.is_admin or request.user.is_superuser)
        )


class AuthorAndStaffOrReadOnly(BasePermission):
    """Права для работы с отзывами и комментариями."""
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
            or request.user.is_admin
            or request.user.is_moderator
            or request.user.is_superuser
        )
