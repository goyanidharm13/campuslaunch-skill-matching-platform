from datetime import timedelta

import pytest
from django.utils import timezone

from accounts.models import User
from opportunities.models import Opportunity, OpportunitySkill, Organization
from skills.models import Skill, StudentSkill
from students.models import StudentProfile


@pytest.fixture
def skills(db):
    return {n: Skill.objects.create(name=n) for n in ["Python", "Django", "MySQL", "JavaScript", "Git", "Docker", "AWS"]}


@pytest.fixture
def student(db, skills):
    user = User.objects.create_user("stu", "stu@x.com", "pass12345", role="student")
    profile = StudentProfile.objects.create(user=user, full_name="Stu Dent", location="Ahmedabad", career_goal="Django developer")
    for n in ["Python", "Django", "MySQL", "JavaScript", "Git"]:
        StudentSkill.objects.create(student=profile, skill=skills[n], level="Intermediate")
    return profile


@pytest.fixture
def recruiter(db):
    user = User.objects.create_user("rec", "rec@x.com", "pass12345", role="recruiter")
    return Organization.objects.create(owner=user, name="Acme Labs", location="Ahmedabad")


@pytest.fixture
def make_opp(recruiter, skills):
    def _make(title="Django Intern", weights=None, days=10, **kw):
        opp = Opportunity.objects.create(organization=recruiter, title=title, opportunity_type="internship",
                                         description="d", location="Ahmedabad",
                                         deadline=timezone.localdate() + timedelta(days=days), **kw)
        weights = weights or {"Python": 3, "Django": 3, "MySQL": 2, "JavaScript": 2, "Git": 1, "Docker": 1}
        for name, w in weights.items():
            OpportunitySkill.objects.create(opportunity=opp, skill=skills[name], weight=w)
        return opp
    return _make


@pytest.fixture(autouse=True)
def _clear_cache():
    from django.core.cache import cache
    cache.clear()
