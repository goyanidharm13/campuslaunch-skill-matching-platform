from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.permissions import student_required
from opportunities.models import Opportunity
from students.models import StudentProfile

from .models import Application
from .services import ApplicationError, apply_to_opportunity


@student_required
@require_POST
def apply(request, pk):
    opp = get_object_or_404(Opportunity.objects.select_related("organization__owner"), pk=pk)
    student = get_object_or_404(StudentProfile, user=request.user)
    try:
        apply_to_opportunity(student, opp, request.POST.get("cover_letter", ""))
        messages.success(request, f"Application sent to {opp.organization.name}.")
    except ApplicationError as exc:
        messages.error(request, str(exc))
    return redirect("opportunities:detail", pk=pk)


@student_required
def my_applications(request):
    student = get_object_or_404(StudentProfile, user=request.user)
    apps = Application.objects.filter(student=student).select_related("opportunity__organization")
    return render(request, "applications/mine.html", {"applications": apps, "statuses": Application.Status.choices})
