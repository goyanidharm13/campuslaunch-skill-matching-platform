from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.permissions import student_required
from students.models import StudentProfile

from .forms import StudentSkillForm
from .models import StudentSkill


@student_required
def manage(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user, defaults={"full_name": request.user.username})
    form = StudentSkillForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        StudentSkill.objects.update_or_create(
            student=profile, skill=data["skill"],
            defaults={"level": data["level"], "years": data["years"]},
        )
        messages.success(request, f"{data['skill'].name} saved to your profile.")
        return redirect("skills:manage")
    my_skills = StudentSkill.objects.filter(student=profile).select_related("skill")
    return render(request, "skills/manage.html", {"form": form, "my_skills": my_skills})


@student_required
@require_POST
def remove(request, pk):
    obj = get_object_or_404(StudentSkill, pk=pk, student__user=request.user)
    obj.delete()
    messages.info(request, "Skill removed.")
    return redirect("skills:manage")
