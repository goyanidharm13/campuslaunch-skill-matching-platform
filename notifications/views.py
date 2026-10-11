from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Notification


@login_required
def notification_list(request):
    items = Notification.objects.filter(user=request.user)[:100]
    return render(request, "notifications/list.html", {"items": items})


@login_required
@require_POST
def mark_read(request, pk):
    get_object_or_404(Notification, pk=pk, user=request.user)
    Notification.objects.filter(pk=pk).update(is_read=True)
    return redirect(request.POST.get("next") or "notifications:list")


@login_required
@require_POST
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect("notifications:list")


@login_required
def unread_count_json(request):
    return JsonResponse({"unread": Notification.objects.filter(user=request.user, is_read=False).count()})
