from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db.models import Count
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from applications.models import Application
from opportunities.models import Opportunity

from .forms import RegisterForm
from .models import User
from .permissions import admin_required


def register(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Welcome to CampusLaunch! Let's set up your account.")
        return redirect("accounts:dashboard")
    return render(request, "accounts/register.html", {"form": form})


@login_required
def dashboard(request):
    """Send each role to its own home screen."""
    if request.user.is_recruiter:
        return redirect("recruiter:dashboard")
    if request.user.is_platform_admin:
        return redirect("accounts:admin_dashboard")
    return redirect("students:dashboard")


@admin_required
def admin_dashboard(request):
    context = {
        "users_by_role": User.objects.values("role").annotate(n=Count("id")).order_by("role"),
        "opps_by_type": Opportunity.objects.values("opportunity_type").annotate(n=Count("id")).order_by("-n"),
        "apps_by_status": Application.objects.values("status").annotate(n=Count("id")).order_by("-n"),
        "total_users": User.objects.count(),
        "total_opps": Opportunity.objects.count(),
        "total_apps": Application.objects.count(),
    }
    return render(request, "accounts/admin_dashboard.html", context)


class ThrottledPasswordResetView(auth_views.PasswordResetView):
    """Django's reset view plus a simple per-IP limit (5 requests / hour) to stop email flooding.
    The response never reveals whether an email address has an account."""
    template_name = "accounts/password_reset_form.html"
    email_template_name = "accounts/password_reset_email.txt"
    subject_template_name = "accounts/password_reset_subject.txt"
    success_url = reverse_lazy("accounts:password_reset_done")
    max_requests = 5
    window_seconds = 3600

    def form_valid(self, form):
        key = f"pwreset:{self.request.META.get('REMOTE_ADDR', 'unknown')}"
        cache.add(key, 0, self.window_seconds)
        if cache.get(key, 0) >= self.max_requests:
            form.add_error(None, "Too many reset requests. Please try again in an hour.")
            return self.form_invalid(form)
        cache.incr(key)
        return super().form_valid(form)
