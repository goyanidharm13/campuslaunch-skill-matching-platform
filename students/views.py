from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.permissions import student_required
from applications.models import Application
from matching.services import recommend

from .forms import CertificationForm, EducationForm, ProfileForm, ProjectForm
from .models import Certification, Education, Project, StudentProfile

SECTIONS = {
    "education": (Education, EducationForm),
    "project": (Project, ProjectForm),
    "certification": (Certification, CertificationForm),
}


def get_profile(user):
    profile, _ = StudentProfile.objects.get_or_create(user=user, defaults={"full_name": user.username})
    return profile


@student_required
def dashboard(request):
    profile = get_profile(request.user)
    recs = recommend(profile, limit=5)
    apps = Application.objects.filter(student=profile).select_related("opportunity__organization")[:5]
    return render(request, "students/dashboard.html", {"profile": profile, "recs": recs, "recent_apps": apps})


@student_required
def profile(request):
    prof = get_profile(request.user)
    context = {
        "profile": prof,
        "educations": prof.educations.all(),
        "projects": prof.projects.all(),
        "certifications": prof.certifications.all(),
        "skills": prof.student_skills.select_related("skill"),
        "education_form": EducationForm(prefix="edu"),
        "project_form": ProjectForm(prefix="proj"),
        "certification_form": CertificationForm(prefix="cert"),
    }
    return render(request, "students/profile.html", context)


@student_required
def profile_edit(request):
    prof = get_profile(request.user)
    form = ProfileForm(request.POST or None, request.FILES or None, instance=prof)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated.")
        return redirect("students:profile")
    return render(request, "students/profile_edit.html", {"form": form})


PREFIX = {"education": "edu", "project": "proj", "certification": "cert"}


@student_required
@require_POST
def section_add(request, kind):
    if kind not in SECTIONS:
        return redirect("students:profile")
    model, form_class = SECTIONS[kind]
    form = form_class(request.POST, prefix=PREFIX[kind])
    if form.is_valid():
        obj = form.save(commit=False)
        obj.student = get_profile(request.user)
        obj.save()
        messages.success(request, f"{kind.title()} added.")
    else:
        errors = "; ".join(f"{k}: {' '.join(v)}" for k, v in form.errors.items())
        messages.error(request, f"Could not add {kind}. {errors}")
    return redirect("students:profile")


@student_required
@require_POST
def section_delete(request, kind, pk):
    if kind not in SECTIONS:
        return redirect("students:profile")
    model, _ = SECTIONS[kind]
    get_object_or_404(model, pk=pk, student__user=request.user).delete()
    messages.info(request, f"{kind.title()} removed.")
    return redirect("students:profile")
