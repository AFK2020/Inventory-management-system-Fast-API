from rest_framework import permissions


class ModifiedAdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):

        if request.method in ["GET"]:
            return True

        elif request.method in ["PUT", "PATCH", "POST", "DELETE"]:
            if request.user.is_authenticated:
                return request.user.is_staff == True

        return False
