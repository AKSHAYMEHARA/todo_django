from rest_framework.permissions import BasePermission


class CustomIsOwnerOrIsAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        try:
            return bool(request.user == obj or request.user.is_staff)

        except Exception as e:
            print(e)

        return False


class CustomIsAdmin(BasePermission):
    def has_permission(self, request, view):
        try:
            return bool(request.user and request.user.is_staff)

        except Exception as e:
            print(e)

        return False
