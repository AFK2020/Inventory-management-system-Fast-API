from rest_framework import permissions


class ModifiedAdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):

        if view.action in ["list", "retrieve"]:
            return True

        elif view.action in [
            "create",
            "update",
            "partial_update",
            "destroy",
            "assign_team_member",
        ]:
            if request.user.is_authenticated:
                return request.user.is_staff == True

        return False
