"""Matching engine: weighted match %, skill-gap analysis, recommendations.
Everything is computed live from current data; nothing is stored."""
from dataclasses import dataclass, field

from django.utils import timezone

from skills.models import StudentSkill


def student_skill_ids(student):
    return set(StudentSkill.objects.filter(student=student).values_list("skill_id", flat=True))


def _ids(student_or_ids):
    return student_or_ids if isinstance(student_or_ids, (set, frozenset)) else student_skill_ids(student_or_ids)


def match_percentage(student_or_ids, opp):
    """match % = matched weight / total weight x 100 (rounded half up)."""
    have = _ids(student_or_ids)
    req = list(opp.opportunityskill_set.all())
    total = sum(r.weight for r in req)
    if total == 0:
        return 0
    got = sum(r.weight for r in req if r.skill_id in have)
    return int(got * 100 / total + 0.5)


@dataclass
class GapResult:
    percent: int
    matched_weight: int
    total_weight: int
    matched: list = field(default_factory=list)   # OpportunitySkill rows the student has
    missing: list = field(default_factory=list)   # OpportunitySkill rows the student lacks

    @property
    def action(self):
        if not self.missing:
            return "You meet every required skill. Apply with confidence."
        names = ", ".join(r.skill.name for r in self.missing)
        return f"Learn {names} to improve your eligibility."


def analyse(student_or_ids, opp):
    have = _ids(student_or_ids)
    req = list(opp.opportunityskill_set.all())
    matched = [r for r in req if r.skill_id in have]
    missing = [r for r in req if r.skill_id not in have]
    total = sum(r.weight for r in req)
    got = sum(r.weight for r in matched)
    pct = int(got * 100 / total + 0.5) if total else 0
    return GapResult(pct, got, total, matched, missing)


@dataclass
class Recommendation:
    opportunity: object
    match: int
    score: float
    missing_count: int


def _goal_bonus(student, opp):
    words = {w for w in (student.career_goal or "").lower().replace("/", " ").split() if len(w) > 2}
    if not words:
        return 0
    haystack = f"{opp.title} {opp.get_opportunity_type_display()}".lower()
    return 10 if any(w in haystack for w in words) else 0


def _location_bonus(student, opp):
    if student.location and opp.location and student.location.lower() == opp.location.lower():
        return 8
    return 4 if opp.is_remote else 0


def _urgency_bonus(opp, today):
    if opp.deadline and 0 <= (opp.deadline - today).days <= 7:
        return 5
    return 0


def recommend(student, limit=10):
    """Rank open opportunities for a student.
    score = 0.7*match + career-goal(10) + location(8) + skill-gap(7) + urgency(5), capped at 100.
    Expired, inactive and already-applied opportunities are excluded."""
    from applications.models import Application
    from opportunities.filters import open_opportunities

    ids = student_skill_ids(student)
    applied = set(Application.objects.filter(student=student).values_list("opportunity_id", flat=True))
    today = timezone.localdate()
    results = []
    for opp in open_opportunities():
        if opp.pk in applied:
            continue
        res = analyse(ids, opp)
        if res.percent == 0:
            continue
        gap_bonus = max(0, 7 - 2 * len(res.missing))
        score = (0.7 * res.percent + _goal_bonus(student, opp) + _location_bonus(student, opp)
                 + gap_bonus + _urgency_bonus(opp, today))
        results.append(Recommendation(opp, res.percent, round(min(score, 100), 1), len(res.missing)))
    results.sort(key=lambda r: (-r.score, -r.match, r.opportunity.title))
    return results[:limit]
