from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, UpdateView
from django.urls import reverse_lazy
from .models import Profile


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "profiles/profile.html"


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = Profile
    fields = ["bio", "avatar", "municipality", "address", "is_teacher", "is_student"]
    template_name = "profiles/profile_edit.html"
    success_url = reverse_lazy("profiles:profile")

    def get_object(self):
        return self.request.user.profile
