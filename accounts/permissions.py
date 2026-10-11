"""Role-based access: decorators for function views, mixins for class views."""
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied


def role_required(*roles):
    """Allow only authenticated users whose role is in `roles`; others get 403."""
    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if request.user.role not in roles:
                raise PermissionDenied("You do not have access to this page.")
            return view(request, *args, **kwargs)
        return login_required(wrapper)
    return decorator


student_required = role_required("student")
recruiter_required = role_required("recruiter")
admin_required = role_required("admin")


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    allowed_roles = ()

    def test_func(self):
        return self.request.user.role in self.allowed_roles


class StudentRequiredMixin(RoleRequiredMixin):
    allowed_roles = ("student",)


class RecruiterRequiredMixin(RoleRequiredMixin):
    allowed_roles = ("recruiter",)
