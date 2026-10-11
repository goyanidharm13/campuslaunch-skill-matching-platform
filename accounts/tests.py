from django.urls import reverse

from accounts.models import User
from students.models import StudentProfile


def test_register_student_creates_profile(client, db):
    resp = client.post(reverse("accounts:register"), {
        "username": "newbie", "email": "n@x.com", "role": "student",
        "password1": "Str0ng-pass-99", "password2": "Str0ng-pass-99"})
    assert resp.status_code == 302
    assert StudentProfile.objects.filter(user__username="newbie").exists()


def test_cannot_self_register_as_admin(client, db):
    client.post(reverse("accounts:register"), {
        "username": "sneaky", "email": "s@x.com", "role": "admin",
        "password1": "Str0ng-pass-99", "password2": "Str0ng-pass-99"})
    assert not User.objects.filter(username="sneaky").exists()


def test_student_cannot_open_recruiter_pages(client, student):
    client.login(username="stu", password="pass12345")
    assert client.get(reverse("recruiter:dashboard")).status_code == 403


def test_recruiter_cannot_open_student_pages(client, recruiter):
    client.login(username="rec", password="pass12345")
    assert client.get(reverse("students:profile")).status_code == 403


def test_anonymous_redirected_to_login(client, db):
    assert client.get(reverse("students:profile")).status_code == 302


# ---- password reset ----
import re


def test_password_reset_full_flow(client, student, mailoutbox):
    resp = client.post(reverse("accounts:password_reset"), {"email": "stu@x.com"})
    assert resp.status_code == 302 and len(mailoutbox) == 1
    link = re.search(r"http://testserver(\S+)", mailoutbox[0].body).group(1)
    first = client.get(link, follow=True)
    set_url = first.redirect_chain[-1][0]
    done = client.post(set_url, {"new_password1": "Brand-new-pass-77", "new_password2": "Brand-new-pass-77"})
    assert done.status_code == 302
    assert client.login(username="stu", password="Brand-new-pass-77")


def test_reset_does_not_reveal_unknown_email(client, db, mailoutbox):
    resp = client.post(reverse("accounts:password_reset"), {"email": "nobody@x.com"})
    assert resp.status_code == 302 and len(mailoutbox) == 0


def test_reset_is_rate_limited(client, student, mailoutbox):
    for _ in range(5):
        client.post(reverse("accounts:password_reset"), {"email": "stu@x.com"})
    resp = client.post(reverse("accounts:password_reset"), {"email": "stu@x.com"})
    assert resp.status_code == 200 and len(mailoutbox) == 5
