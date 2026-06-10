from django.urls import path
from . import views

app_name = "messaging"

urlpatterns = [
    path("", views.ConversationListView.as_view(), name="list"),
    path("<int:pk>/", views.ConversationDetailView.as_view(), name="detail"),
    path("start/<int:teacher_pk>/", views.StartConversationView.as_view(), name="start"),
]
