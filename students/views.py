from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, UpdateView
from django.urls import reverse_lazy
from .models import StudentProfile


class StudentProfileView(LoginRequiredMixin, TemplateView):
    template_name = "students/profile.html"


class StudentProfileEditView(LoginRequiredMixin, UpdateView):
    model = StudentProfile
    fields = ["learning_goals"]
    template_name = "students/profile_edit.html"
    success_url = reverse_lazy("students:profile")

    def get_object(self):
        return self.request.user.profile.student_profile
