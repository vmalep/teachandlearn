from django.urls import path
from . import views

urlpatterns = [
    path("", views.TeacherDirectoryView.as_view(), name="home"),
    path("teachers/<int:pk>/", views.TeacherDetailView.as_view(), name="teacher-detail"),
    path("teachers/<int:teacher_pk>/offerings/<int:pk>/", views.OfferingDetailView.as_view(), name="offering-detail"),
    path("map/", views.MapView.as_view(), name="map"),
    path("map/data/", views.MapDataView.as_view(), name="map-data"),
]
