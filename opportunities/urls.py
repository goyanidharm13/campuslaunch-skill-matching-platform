from django.urls import path

from . import views

app_name = "opportunities"

urlpatterns = [
    path("", views.opportunity_list, name="list"),
    path("recommended/", views.recommendations, name="recommended"),
    path("saved/", views.saved_list, name="saved"),
    path("<int:pk>/", views.opportunity_detail, name="detail"),
    path("<int:pk>/save/", views.toggle_save, name="toggle_save"),
]
