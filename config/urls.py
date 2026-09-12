from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.views.generic import TemplateView
from .sitemaps import StaticViewSitemap

sitemaps = {"static": StaticViewSitemap()}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
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
