from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("opportunities", views.OpportunityViewSet, basename="opportunity")
router.register("skills", views.SkillViewSet, basename="skill")
router.register("applications", views.ApplicationViewSet, basename="application")
router.register("notifications", views.NotificationViewSet, basename="notification")

urlpatterns = [
    path("profile/", views.ProfileView.as_view(), name="api-profile"),
    path("recommended/", views.RecommendedView.as_view(), name="api-recommended"),
    path("matching/<int:pk>/", views.MatchingView.as_view(), name="api-matching"),
    path("skill-gap/<int:pk>/", views.SkillGapView.as_view(), name="api-skill-gap"),
    path("", include(router.urls)),
]
