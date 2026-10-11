from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from applications.models import Application
from notifications.models import Notification
from notifications.services import notify
from opportunities.models import SavedOpportunity
from opportunities.filters import open_opportunities


class Command(BaseCommand):
    help = "Notify students who saved an opportunity (and have not applied) when its deadline is near."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=3)

    def handle(self, *args, **opts):
        today = timezone.localdate()
        limit = today + timedelta(days=opts["days"])
        sent = 0
        for opp in open_opportunities().filter(deadline__isnull=False, deadline__lte=limit):
            applied = set(Application.objects.filter(opportunity=opp).values_list("student_id", flat=True))
            for saved in SavedOpportunity.objects.filter(opportunity=opp).select_related("student__user"):
                if saved.student_id in applied:
                    continue
                msg = f"Deadline near: {opp.title} closes on {opp.deadline:%d %b}"
                if Notification.objects.filter(user=saved.student.user, message=msg).exists():
                    continue
                notify(saved.student.user, msg, f"/opportunities/{opp.pk}/")
                sent += 1
        self.stdout.write(self.style.SUCCESS(f"{sent} deadline alert(s) sent."))
