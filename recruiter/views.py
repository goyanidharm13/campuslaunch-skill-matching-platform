from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.permissions import recruiter_required
from applications.models import Application
from applications.services import ApplicationError, change_status
from matching.services import analyse, student_skill_ids
from notifications.services import notify_relevant_students
from opportunities.forms import OpportunityForm, OpportunitySkillFormSet, OrganizationForm
from opportunities.models import Opportunity, Organization
from skills.models import StudentSkill


def _org_or_none(user):
    return Organization.objects.filter(owner=user).first()


def _require_org(request):
    org = _org_or_none(request.user)
    if org is None:
        messages.info(request, "Set up your organization before posting opportunities.")
    return org


@recruiter_required
def dashboard(request):
    org = _org_or_none(request.user)
    if org is None:
        return redirect("recruiter:organization")
    apps = Application.objects.filter(opportunity__organization=org)
    stats = {
        "total": org.opportunities.count(),
        "active": org.opportunities.filter(is_active=True).count(),
        "applicants": apps.count(),
        "shortlisted": apps.filter(status=Application.Status.SHORTLISTED).count(),
        "selected": apps.filter(status=Application.Status.SELECTED).count(),
    }
    performance = (org.opportunities.annotate(
        applicants=Count("applications"),
        shortlisted=Count("applications", filter=Q(applications__status="Shortlisted")),
        selected=Count("applications", filter=Q(applications__status="Selected")),
    ).order_by("-applicants", "-created_at"))
    recent = apps.select_related("student", "opportunity")[:8]
    return render(request, "recruiter/dashboard.html",
                  {"org": org, "stats": stats, "performance": performance, "recent": recent})


@recruiter_required
def organization(request):
    instance = _org_or_none(request.user)
    form = OrganizationForm(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        org = form.save(commit=False)
        org.owner = request.user
        org.save()
        messages.success(request, "Organization saved.")
        return redirect("recruiter:dashboard")
    return render(request, "recruiter/organization.html", {"form": form})


@recruiter_required
def opportunity_form(request, pk=None):
    org = _require_org(request)
    if org is None:
        return redirect("recruiter:organization")
    instance = get_object_or_404(Opportunity, pk=pk, organization=org) if pk else None
    form = OpportunityForm(request.POST or None, instance=instance)
    formset = OpportunitySkillFormSet(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid() and formset.is_valid():
        with transaction.atomic():
            opp = form.save(commit=False)
            opp.organization = org
            opp.save()
            formset.instance = opp
            formset.save()
        if instance is None and opp.is_active:
            sent = notify_relevant_students(opp)
            messages.success(request, f"Posted. {sent} matching student(s) were notified.")
        else:
            messages.success(request, "Opportunity updated.")
        return redirect("recruiter:dashboard")
    return render(request, "recruiter/opportunity_form.html",
                  {"form": form, "formset": formset, "editing": instance})


@recruiter_required
@require_POST
def opportunity_toggle(request, pk):
    opp = get_object_or_404(Opportunity, pk=pk, organization__owner=request.user)
    opp.is_active = not opp.is_active
    opp.save(update_fields=["is_active"])
    messages.info(request, f"{opp.title} is now {'active' if opp.is_active else 'closed'}.")
    return redirect("recruiter:dashboard")


@recruiter_required
def applicants(request, pk):
    opp = get_object_or_404(
        Opportunity.objects.prefetch_related("opportunityskill_set__skill"), pk=pk, organization__owner=request.user)
    apps = (Application.objects.filter(opportunity=opp)
            .select_related("student__user")
            .annotate(extras=Count("student__projects", distinct=True) + Count("student__educations", distinct=True)
                      + Count("student__certifications", distinct=True)))
    have = {}
    for sid, kid in StudentSkill.objects.filter(student__applications__opportunity=opp).values_list("student_id", "skill_id"):
        have.setdefault(sid, set()).add(kid)
    rows = []
    for a in apps:
        res = analyse(have.get(a.student_id, set()), opp)
        a.result = res
        rows.append(a)
    # match % > skill coverage > projects/experience > application date
    rows.sort(key=lambda a: (-a.result.percent, -len(a.result.matched), -a.extras, a.applied_at))
    for i, a in enumerate(rows, start=1):
        a.rank = i
    return render(request, "recruiter/applicants.html",
                  {"opp": opp, "rows": rows, "statuses": Application.Status.choices})


@recruiter_required
@require_POST
def update_status(request, pk):
    app = get_object_or_404(Application.objects.select_related("opportunity", "student__user"),
                            pk=pk, opportunity__organization__owner=request.user)
    try:
        change_status(app, request.POST.get("status", ""))
        messages.success(request, f"{app.student} moved to {app.status}.")
    except ApplicationError as exc:
        messages.error(request, str(exc))
    return redirect("recruiter:applicants", pk=app.opportunity_id)


@recruiter_required
def student_detail(request, pk):
    """A recruiter may only open profiles of students who applied to their own opportunities."""
    app = get_object_or_404(Application.objects.select_related("student__user", "opportunity"),
                            pk=pk, opportunity__organization__owner=request.user)
    s = app.student
    return render(request, "recruiter/student_detail.html", {
        "app": app, "s": s, "skills": s.student_skills.select_related("skill"),
        "educations": s.educations.all(), "projects": s.projects.all(), "certifications": s.certifications.all(),
    })
