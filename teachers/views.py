from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, TemplateView, UpdateView
from django.urls import reverse_lazy
from .models import TeacherProfile


class TeacherDirectoryView(ListView):
    model = TeacherProfile
    template_name = "teachers/directory.html"
    context_object_name = "teachers"

    def get_queryset(self):
        qs = TeacherProfile.objects.filter(state=TeacherProfile.State.VALIDATED).select_related(
            "profile__user"
        ).prefetch_related("subjects")
        subject = self.request.GET.get("subject")
        municipality = self.request.GET.get("municipality")
        max_price = self.request.GET.get("max_price")
        if subject:
            qs = qs.filter(subjects__id=subject)
        if municipality:
            qs = qs.filter(profile__municipality__icontains=municipality)
        if max_price:
            qs = qs.filter(price_per_hour__lte=max_price)
        return qs


class TeacherDetailView(LoginRequiredMixin, DetailView):
    model = TeacherProfile
    template_name = "teachers/detail.html"
    context_object_name = "teacher"

    def get_queryset(self):
        return TeacherProfile.objects.filter(state=TeacherProfile.State.VALIDATED).select_related(
            "profile__user"
        ).prefetch_related("subjects", "certificates")


class TeacherProfileView(LoginRequiredMixin, TemplateView):
    template_name = "teachers/profile.html"


class TeacherProfileEditView(LoginRequiredMixin, UpdateView):
    model = TeacherProfile
    fields = ["subjects", "native_language", "price_per_hour", "availability"]
    template_name = "teachers/profile_edit.html"
    success_url = reverse_lazy("teachers:profile")

    def get_object(self):
        return self.request.user.profile.teacher_profile
