from django.urls import path
from . import views

app_name = "profiles"

urlpatterns = [
    path("", views.ProfileView.as_view(), name="profile"),
    path("edit/", views.ProfileEditView.as_view(), name="edit"),
    path("municipalities/", views.MunicipalityLookupView.as_view(), name="municipalities"),
]
