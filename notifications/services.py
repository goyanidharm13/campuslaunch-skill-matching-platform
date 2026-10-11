from django.utils import timezone

from .models import Notification


def notify(user, message, link=""):
    return Notification.objects.create(user=user, message=message[:255], link=link)


def notify_relevant_students(opp, threshold=50):
    """Tell students who match a new opportunity well. One bulk insert."""
    from matching.services import match_percentage
    from skills.models import StudentSkill
    from students.models import StudentProfile

    have = {}
    for sid, kid in StudentSkill.objects.values_list("student_id", "skill_id"):
        have.setdefault(sid, set()).add(kid)
    opp_ready = type(opp).objects.prefetch_related("opportunityskill_set").get(pk=opp.pk)
    link = f"/opportunities/{opp.pk}/"
    rows = []
    for sid, user_id in StudentProfile.objects.values_list("id", "user_id"):
        pct = match_percentage(have.get(sid, set()), opp_ready)
        if pct >= threshold:
            rows.append(Notification(user_id=user_id, link=link,
                                     message=f"New {opp.get_opportunity_type_display().lower()}: {opp.title} ({pct}% match)"))
    Notification.objects.bulk_create(rows)
    return len(rows)
