from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory
from django.utils import timezone

from .models import Opportunity, Organization, OpportunitySkill


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ("name", "website", "location", "description")
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}


class OpportunityForm(forms.ModelForm):
    class Meta:
        model = Opportunity
        fields = ("title", "opportunity_type", "description", "location", "is_remote",
                  "compensation", "deadline", "is_active")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "deadline": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }

    def clean_deadline(self):
        deadline = self.cleaned_data.get("deadline")
        if deadline and deadline < timezone.localdate() and not self.instance.pk:
            raise forms.ValidationError("The deadline cannot be in the past.")
        return deadline


class BaseSkillFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        kept = [f for f in self.forms
                if f.cleaned_data and not f.cleaned_data.get("DELETE") and f.cleaned_data.get("skill")]
        if not kept:
            raise forms.ValidationError("Add at least one required skill with a weight.")


OpportunitySkillFormSet = inlineformset_factory(
    Opportunity, OpportunitySkill, formset=BaseSkillFormSet,
    fields=("skill", "weight"), extra=3, can_delete=True,
    widgets={"weight": forms.NumberInput(attrs={"min": 1, "max": 5})},
)
