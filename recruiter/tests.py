from django.urls import reverse

from accounts.models import User
from applications.services import apply_to_opportunity
from opportunities.models import Organization


def test_applicants_ranked_by_match(client, student, make_opp, skills, recruiter):
    from skills.models import StudentSkill
    from students.models import StudentProfile
    opp = make_opp()
    other_user = User.objects.create_user("weak", "w@x.com", "pass12345", role="student")
    weak = StudentProfile.objects.create(user=other_user, full_name="Weak Student")
    StudentSkill.objects.create(student=weak, skill=skills["Git"])
    apply_to_opportunity(weak, opp)
    apply_to_opportunity(student, opp)
    client.login(username="rec", password="pass12345")
    rows = client.get(reverse("recruiter:applicants", args=[opp.pk])).context["rows"]
    assert [r.student.full_name for r in rows] == ["Stu Dent", "Weak Student"]


def test_recruiter_cannot_see_other_orgs_applicants(client, make_opp, recruiter):
    opp = make_opp()
    intruder = User.objects.create_user("rec2", "r2@x.com", "pass12345", role="recruiter")
    Organization.objects.create(owner=intruder, name="Other Co")
    client.login(username="rec2", password="pass12345")
    assert client.get(reverse("recruiter:applicants", args=[opp.pk])).status_code == 404


def test_status_update_by_owner(client, student, make_opp, recruiter):
    app = apply_to_opportunity(student, make_opp())
    client.login(username="rec", password="pass12345")
    client.post(reverse("recruiter:update_status", args=[app.pk]), {"status": "Interview"})
    app.refresh_from_db()
    assert app.status == "Interview"
