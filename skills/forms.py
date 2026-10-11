from django import forms

from .models import StudentSkill


class StudentSkillForm(forms.ModelForm):
    class Meta:
        model = StudentSkill
        fields = ("skill", "level", "years")
        widgets = {"years": forms.NumberInput(attrs={"step": "0.5", "min": "0", "max": "40"})}

    def clean_years(self):
        years = self.cleaned_data["years"]
        if years < 0 or years > 40:
            raise forms.ValidationError("Years must be between 0 and 40.")
        return years
