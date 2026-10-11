import django_filters as df
from django.db.models import Q
from django.utils import timezone

from skills.models import StudentSkill

from .models import Opportunity


class OpportunityFilter(df.FilterSet):
    q = df.CharFilter(method="filter_q", label="Search")
    type = df.ChoiceFilter(field_name="opportunity_type", choices=Opportunity.Type.choices)
    location = df.CharFilter(field_name="location", lookup_expr="icontains")
    remote = df.BooleanFilter(field_name="is_remote", label="Remote only", method="filter_remote")
    deadline_before = df.DateFilter(field_name="deadline", lookup_expr="lte")
    deadline_after = df.DateFilter(field_name="deadline", lookup_expr="gte")
    relevant = df.BooleanFilter(method="filter_relevant", label="Matching my skills")

    class Meta:
        model = Opportunity
        fields = []

    def filter_q(self, qs, name, value):
        value = (value or "").strip()
        if not value:
            return qs
        return qs.filter(Q(title__icontains=value) | Q(skills__name__icontains=value)
                         | Q(organization__name__icontains=value)).distinct()

    def filter_remote(self, qs, name, value):
        return qs.filter(is_remote=True) if value else qs

    def filter_relevant(self, qs, name, value):
        user = getattr(self.request, "user", None)
        if not value or not user or not user.is_authenticated or not user.is_student:
            return qs
        ids = StudentSkill.objects.filter(student__user=user).values_list("skill_id", flat=True)
        return qs.filter(skills__id__in=list(ids)).distinct()


def open_opportunities():
    """Active opportunities whose deadline has not passed."""
    today = timezone.localdate()
    return (Opportunity.objects.filter(is_active=True)
            .filter(Q(deadline__isnull=True) | Q(deadline__gte=today))
            .select_related("organization")
            .prefetch_related("opportunityskill_set__skill"))
