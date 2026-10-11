from matching.services import analyse, match_percentage, recommend


def test_weighted_match_matches_slide_example(student, make_opp):
    opp = make_opp()  # 11 of 12 weight matched (Docker missing)
    assert match_percentage(student, opp) == 92


def test_skill_gap_lists_missing_and_action(student, make_opp):
    opp = make_opp("Cloud", {"Python": 1, "Django": 1, "MySQL": 1, "JavaScript": 1, "Docker": 1, "AWS": 1})
    res = analyse(student, opp)
    assert res.percent == 67
    assert {r.skill.name for r in res.missing} == {"Docker", "AWS"}
    assert "Docker" in res.action and "AWS" in res.action


def test_no_requirements_means_zero(student, make_opp, skills):
    opp = make_opp("Empty", {"Docker": 1})
    opp.opportunityskill_set.all().delete()
    assert match_percentage(student, opp) == 0


def test_recommendations_exclude_expired_inactive_and_applied(student, make_opp):
    good = make_opp("Good")
    make_opp("Expired", days=-2)
    make_opp("Inactive", is_active=False)
    applied = make_opp("Applied")
    from applications.services import apply_to_opportunity
    apply_to_opportunity(student, applied)
    titles = [r.opportunity.title for r in recommend(student)]
    assert titles == ["Good"]
    assert recommend(student)[0].opportunity == good
