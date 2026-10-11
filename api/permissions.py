from rest_framework.permissions import BasePermission


class IsStudent(BasePermission):
    message = "Only students can use this endpoint."

    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and u.role == "student")
