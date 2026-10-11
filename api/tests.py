from django.urls import reverse


def test_api_requires_auth(client, db):
    assert client.get("/api/opportunities/").status_code in (401, 403)


def test_opportunity_list_includes_match(client, student, make_opp):
    make_opp()
    client.login(username="stu", password="pass12345")
    data = client.get("/api/opportunities/").json()
    assert data["results"][0]["match_percentage"] == 92


def test_apply_via_api_and_duplicate_rejected(client, student, make_opp):
    opp = make_opp()
    client.login(username="stu", password="pass12345")
    assert client.post("/api/applications/", {"opportunity": opp.pk}).status_code == 201
    assert client.post("/api/applications/", {"opportunity": opp.pk}).status_code == 400


def test_skill_gap_endpoint(client, student, make_opp):
    opp = make_opp()
    client.login(username="stu", password="pass12345")
    data = client.get(f"/api/skill-gap/{opp.pk}/").json()
    assert data["match_percentage"] == 92 and data["missing"][0]["skill"] == "Docker"


def test_recruiter_blocked_from_student_endpoints(client, recruiter):
    client.login(username="rec", password="pass12345")
    assert client.get("/api/profile/").status_code == 403
