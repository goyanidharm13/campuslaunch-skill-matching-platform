from rest_framework import serializers

from applications.models import Application
from applications.services import ApplicationError, apply_to_opportunity
from matching.services import match_percentage, student_skill_ids
from notifications.models import Notification
from opportunities.models import Opportunity, OpportunitySkill
from skills.models import Skill, StudentSkill
from students.models import StudentProfile


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ("id", "name", "category")


class OpportunitySkillSerializer(serializers.ModelSerializer):
    skill = serializers.CharField(source="skill.name")
    skill_id = serializers.IntegerField(source="skill.id")

    class Meta:
        model = OpportunitySkill
        fields = ("skill_id", "skill", "weight")


class OpportunitySerializer(serializers.ModelSerializer):
    organization = serializers.CharField(source="organization.name")
    type = serializers.CharField(source="opportunity_type")
    required_skills = OpportunitySkillSerializer(source="opportunityskill_set", many=True, read_only=True)
    match_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Opportunity
        fields = ("id", "title", "type", "organization", "description", "location", "is_remote",
                  "compensation", "deadline", "required_skills", "match_percentage")

    def get_match_percentage(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated or request.user.role != "student":
            return None
        if "_skill_ids" not in self.context:  # one query per request, not per row
            self.context["_skill_ids"] = student_skill_ids_for(request.user)
        return match_percentage(self.context["_skill_ids"], obj)


def student_skill_ids_for(user):
    profile = StudentProfile.objects.filter(user=user).first()
    return student_skill_ids(profile) if profile else set()


class ApplicationSerializer(serializers.ModelSerializer):
    opportunity_title = serializers.CharField(source="opportunity.title", read_only=True)

    class Meta:
        model = Application
        fields = ("id", "opportunity", "opportunity_title", "status", "cover_letter", "applied_at")
        read_only_fields = ("status", "applied_at")

    def create(self, validated_data):
        student = StudentProfile.objects.get(user=self.context["request"].user)
        try:
            return apply_to_opportunity(student, validated_data["opportunity"], validated_data.get("cover_letter", ""))
        except ApplicationError as exc:
            raise serializers.ValidationError({"detail": str(exc)})


class StudentSkillSerializer(serializers.ModelSerializer):
    skill = serializers.CharField(source="skill.name")

    class Meta:
        model = StudentSkill
        fields = ("skill", "level", "years")


class ProfileSerializer(serializers.ModelSerializer):
    skills = StudentSkillSerializer(source="student_skills", many=True, read_only=True)
    completeness = serializers.IntegerField(read_only=True)

    class Meta:
        model = StudentProfile
        fields = ("full_name", "phone", "location", "bio", "career_goal", "github_url",
                  "linkedin_url", "portfolio_url", "skills", "completeness")


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ("id", "message", "link", "created_at", "is_read")
