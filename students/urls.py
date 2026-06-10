from django.urls import path
from . import views

app_name = "students"

urlpatterns = [
    path("profile/", views.StudentProfileView.as_view(), name="profile"),
    path("profile/edit/", views.StudentProfileEditView.as_view(), name="profile-edit"),
]
