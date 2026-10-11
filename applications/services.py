"""Application workflow: logged in? active? deadline OK? no duplicate? -> create 'Applied' -> notify both."""
from django.db import IntegrityError, transaction

from notifications.services import notify

from .models import Application


class ApplicationError(Exception):
    """Raised with a user-friendly message when an application is not allowed."""


@transaction.atomic
def apply_to_opportunity(student, opp, cover_letter=""):
    if not opp.is_active:
        raise ApplicationError("This opportunity is no longer active.")
    if opp.is_expired:
        raise ApplicationError("The deadline for this opportunity has passed.")
    if Application.objects.filter(student=student, opportunity=opp).exists():
        raise ApplicationError("You have already applied to this opportunity.")
    try:
        with transaction.atomic():
            app = Application.objects.create(student=student, opportunity=opp, cover_letter=cover_letter[:2000])
    except IntegrityError:  # race: unique constraint is the last line of defence
        raise ApplicationError("You have already applied to this opportunity.")
    notify(student.user, f"You applied to {opp.title} at {opp.organization.name}.", f"/opportunities/{opp.pk}/")
    notify(opp.organization.owner, f"New application from {student} for {opp.title}.", f"/recruiter/opportunities/{opp.pk}/applicants/")
    return app


FLOW = [s for s, _ in Application.Status.choices]


@transaction.atomic
def change_status(application, new_status):
    if new_status not in dict(Application.Status.choices):
        raise ApplicationError("Unknown status.")
    if application.status == new_status:
        return application
    application.status = new_status
    application.save(update_fields=["status", "updated_at"])
    opp = application.opportunity
    notify(application.student.user, f"Your application for {opp.title} is now: {new_status}.", f"/opportunities/{opp.pk}/")
    return application
