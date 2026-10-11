from django.urls import path

from . import views

app_name = "recruiter"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("organization/", views.organization, name="organization"),
    path("opportunities/new/", views.opportunity_form, name="opportunity_new"),
    path("opportunities/<int:pk>/edit/", views.opportunity_form, name="opportunity_edit"),
    path("opportunities/<int:pk>/toggle/", views.opportunity_toggle, name="opportunity_toggle"),
    path("opportunities/<int:pk>/applicants/", views.applicants, name="applicants"),
    path("applications/<int:pk>/status/", views.update_status, name="update_status"),
    path("applications/<int:pk>/student/", views.student_detail, name="student_detail"),
]
