from django.urls import path

from . import views

app_name = "students"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("profile/<str:kind>/add/", views.section_add, name="section_add"),
    path("profile/<str:kind>/<int:pk>/delete/", views.section_delete, name="section_delete"),
]
