from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from applications.models import Application
from matching.services import analyse, recommend
from notifications.models import Notification
from opportunities.filters import OpportunityFilter, open_opportunities
from skills.models import Skill
from students.models import StudentProfile

from .permissions import IsStudent
from .serializers import (ApplicationSerializer, NotificationSerializer, OpportunitySerializer,
                          ProfileSerializer, SkillSerializer)


class OpportunityViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OpportunitySerializer
    filterset_class = OpportunityFilter

    def get_queryset(self):
        return open_opportunities()


class SkillViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    search_fields = ("name",)
    pagination_class = None


class ApplicationViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):
    serializer_class = ApplicationSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        return Application.objects.filter(student__user=self.request.user).select_related("opportunity")


class NotificationViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        qs = Notification.objects.filter(user=self.request.user)
        if self.request.query_params.get("unread") in ("1", "true"):
            qs = qs.filter(is_read=False)
        return qs


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsStudent]

    def get_object(self):
        return get_object_or_404(StudentProfile, user=self.request.user)


class RecommendedView(APIView):
    permission_classes = [IsStudent]

    def get(self, request):
        profile = get_object_or_404(StudentProfile, user=request.user)
        data = [{"opportunity_id": r.opportunity.pk, "title": r.opportunity.title, "match_percentage": r.match,
                 "score": r.score, "missing_skills": r.missing_count} for r in recommend(profile, limit=10)]
        return Response(data)


class MatchingView(APIView):
    permission_classes = [IsStudent]

    def get(self, request, pk):
        profile = get_object_or_404(StudentProfile, user=request.user)
        opp = get_object_or_404(open_opportunities(), pk=pk)
        res = analyse(profile, opp)
        return Response({"opportunity_id": opp.pk, "match_percentage": res.percent,
                         "matched_weight": res.matched_weight, "total_weight": res.total_weight})


class SkillGapView(APIView):
    permission_classes = [IsStudent]

    def get(self, request, pk):
        profile = get_object_or_404(StudentProfile, user=request.user)
        opp = get_object_or_404(open_opportunities(), pk=pk)
        res = analyse(profile, opp)
        return Response({
            "opportunity_id": opp.pk, "match_percentage": res.percent,
            "matched": [r.skill.name for r in res.matched],
            "missing": [{"skill": r.skill.name, "weight": r.weight} for r in res.missing],
            "action": res.action,
        })
