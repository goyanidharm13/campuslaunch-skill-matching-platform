from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.permissions import student_required
from applications.models import Application
from matching.services import analyse, match_percentage, recommend, student_skill_ids
from students.models import StudentProfile

from .filters import OpportunityFilter, open_opportunities
from .models import Opportunity, SavedOpportunity


def _student(user):
    if user.is_authenticated and user.is_student:
        return StudentProfile.objects.filter(user=user).first()
    return None


def home(request):
    student = _student(request.user)
    latest = open_opportunities()[:6]
    ctx = {
        "latest": latest,
        "types": Opportunity.Type.choices,
        "recs": recommend(student, limit=3) if student else [],
        "open_count": open_opportunities().count(),
    }
    return render(request, "home.html", ctx)


def opportunity_list(request):
    student = _student(request.user)
    f = OpportunityFilter(request.GET or None, queryset=open_opportunities(), request=request)
    page = Paginator(f.qs, 9).get_page(request.GET.get("page"))
    if student:
        ids = student_skill_ids(student)
        for opp in page:
            opp.match = match_percentage(ids, opp)
    params = request.GET.copy()
    params.pop("page", None)
    return render(request, "opportunities/list.html", {"filter": f, "page": page, "querystring": params.urlencode(), "types": Opportunity.Type.choices})


def opportunity_detail(request, pk):
    opp = get_object_or_404(
        Opportunity.objects.select_related("organization").prefetch_related("opportunityskill_set__skill"), pk=pk)
    if not opp.is_active and not (request.user.is_authenticated and opp.organization.owner_id == request.user.id):
        raise Http404("This opportunity is no longer available.")
    student = _student(request.user)
    ctx = {"opp": opp, "requirements": opp.opportunityskill_set.all(), "student": student}
    if student:
        ctx.update(
            analysis=analyse(student, opp),
            applied=Application.objects.filter(student=student, opportunity=opp).first(),
            is_saved=SavedOpportunity.objects.filter(student=student, opportunity=opp).exists(),
        )
    return render(request, "opportunities/detail.html", ctx)


@student_required
@require_POST
def toggle_save(request, pk):
    opp = get_object_or_404(Opportunity, pk=pk)
    student = get_object_or_404(StudentProfile, user=request.user)
    obj, created = SavedOpportunity.objects.get_or_create(student=student, opportunity=opp)
    if not created:
        obj.delete()
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"saved": created})
    messages.success(request, "Saved for later." if created else "Removed from saved.")
    return redirect("opportunities:detail", pk=pk)


@student_required
def saved_list(request):
    student = get_object_or_404(StudentProfile, user=request.user)
    items = SavedOpportunity.objects.filter(student=student).select_related("opportunity__organization")
    return render(request, "opportunities/saved.html", {"items": items})


@login_required
def recommendations(request):
    student = _student(request.user)
    if not student:
        return redirect("opportunities:list")
    return render(request, "opportunities/recommended.html", {"recs": recommend(student, limit=20)})
