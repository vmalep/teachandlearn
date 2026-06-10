from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView
from .forms import ProfileForm
from .models import Profile


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "profiles/profile.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        profile = self.request.user.profile
        ctx["profile"] = profile
        ctx["teacher_profile"] = getattr(profile, "teacher_profile", None)
        ctx["student_profile"] = getattr(profile, "student_profile", None)
        return ctx


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = "profiles/profile_edit.html"
    success_url = reverse_lazy("profiles:profile")

    def get_object(self):
        return self.request.user.profile

    def form_valid(self, form):
        response = super().form_valid(form)
        profile = form.instance
        if profile.is_teacher:
            from teachers.models import TeacherProfile
            TeacherProfile.objects.get_or_create(profile=profile)
        if profile.is_student:
            from students.models import StudentProfile
            StudentProfile.objects.get_or_create(profile=profile)
        return response
