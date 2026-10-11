from django.urls import reverse

from opportunities.filters import OpportunityFilter, open_opportunities


def test_search_by_skill_name_and_type(make_opp):
    make_opp("Django Intern")
    qs = OpportunityFilter({"q": "mysql", "type": "internship"}, queryset=open_opportunities()).qs
    assert qs.count() == 1


def test_list_hides_expired(client, make_opp):
    make_opp("Visible")
    make_opp("Hidden", days=-3)
    html = client.get(reverse("opportunities:list")).content.decode()
    assert "Visible" in html and "Hidden" not in html


def test_detail_shows_match_for_student(client, student, make_opp):
    opp = make_opp()
    client.login(username="stu", password="pass12345")
    assert "92%" in client.get(reverse("opportunities:detail", args=[opp.pk])).content.decode()
