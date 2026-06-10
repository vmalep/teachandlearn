from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("accounts/", include("accounts.urls")),
    path("profiles/", include("profiles.urls")),
    path("teachers/", include("teachers.urls")),
    path("students/", include("students.urls")),
    path("messages/", include("messaging.urls")),
    path("reviews/", include("reviews.urls")),
    path("", include("teachers.urls_public")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
