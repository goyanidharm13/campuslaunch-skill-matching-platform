from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from opportunities.views import home

urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("students/", include("students.urls")),
    path("skills/", include("skills.urls")),
    path("opportunities/", include("opportunities.urls")),
    path("applications/", include("applications.urls")),
    path("recruiter/", include("recruiter.urls")),
    path("notifications/", include("notifications.urls")),
    path("api/", include("api.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
