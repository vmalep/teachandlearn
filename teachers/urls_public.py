from django.urls import path
from . import views

urlpatterns = [
    path("", views.TeacherDirectoryView.as_view(), name="home"),
    path("teachers/<int:pk>/", views.TeacherDetailView.as_view(), name="teacher-detail"),
]
