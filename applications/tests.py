import pytest

from applications.models import Application
from applications.services import ApplicationError, apply_to_opportunity, change_status
from notifications.models import Notification


def test_apply_creates_application_and_notifies_both(student, make_opp):
    opp = make_opp()
    app = apply_to_opportunity(student, opp)
    assert app.status == "Applied"
    assert Notification.objects.filter(user=student.user).count() == 1
    assert Notification.objects.filter(user=opp.organization.owner).count() == 1


def test_duplicate_application_blocked(student, make_opp):
    opp = make_opp()
    apply_to_opportunity(student, opp)
    with pytest.raises(ApplicationError):
        apply_to_opportunity(student, opp)
    assert Application.objects.count() == 1


def test_expired_and_inactive_blocked(student, make_opp):
    with pytest.raises(ApplicationError):
        apply_to_opportunity(student, make_opp("Old", days=-1))
    with pytest.raises(ApplicationError):
        apply_to_opportunity(student, make_opp("Off", is_active=False))


def test_status_change_notifies_student(student, make_opp):
    app = apply_to_opportunity(student, make_opp())
    change_status(app, "Shortlisted")
    app.refresh_from_db()
    assert app.status == "Shortlisted"
    assert Notification.objects.filter(user=student.user, message__contains="Shortlisted").exists()
