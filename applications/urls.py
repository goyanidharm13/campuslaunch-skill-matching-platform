from django.urls import path

from . import views

app_name = "applications"

urlpatterns = [
    path("", views.my_applications, name="mine"),
    path("apply/<int:pk>/", views.apply, name="apply"),
]
