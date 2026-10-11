from django.urls import path

from . import views

app_name = "skills"

urlpatterns = [
    path("", views.manage, name="manage"),
    path("<int:pk>/remove/", views.remove, name="remove"),
]
