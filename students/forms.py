from django import forms

from .models import Certification, Education, Project, StudentProfile


class DateInput(forms.DateInput):
    input_type = "date"

    def __init__(self, **kw):
        super().__init__(format="%Y-%m-%d", **kw)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ("full_name", "phone", "location", "bio", "career_goal", "github_url",
                  "linkedin_url", "portfolio_url", "image", "resume")
        widgets = {"bio": forms.Textarea(attrs={"rows": 3})}


class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ("degree", "institution", "field_of_study", "start_date", "end_date", "grade")
        widgets = {"start_date": DateInput(), "end_date": DateInput()}

    def clean(self):
        data = super().clean()
        s, e = data.get("start_date"), data.get("end_date")
        if s and e and e < s:
            self.add_error("end_date", "End date cannot be before the start date.")
        return data


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ("title", "description", "technologies", "github_url", "live_url")
        widgets = {"description": forms.Textarea(attrs={"rows": 2})}


class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ("name", "issuer", "issued_on", "credential_url")
        widgets = {"issued_on": DateInput()}
