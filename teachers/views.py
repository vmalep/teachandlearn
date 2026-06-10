from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView
from .forms import CertificateFormSet, TeacherProfileForm
from .models import TeacherProfile
from subjects.models import Subject


class TeacherDirectoryView(ListView):
    model = TeacherProfile
    template_name = "teachers/directory.html"
    context_object_name = "teachers"

    def get_queryset(self):
        qs = (
            TeacherProfile.objects.filter(state=TeacherProfile.State.VALIDATED)
            .select_related("profile__user")
            .prefetch_related("subjects")
        )
        subject = self.request.GET.get("subject")
        municipality = self.request.GET.get("municipality")
        max_price = self.request.GET.get("max_price")
        if subject:
            qs = qs.filter(subjects__id=subject)
        if municipality:
            qs = qs.filter(profile__municipality__icontains=municipality)
        if max_price:
            try:
                qs = qs.filter(price_per_hour__lte=float(max_price))
            except ValueError:
                pass
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["all_subjects"] = Subject.objects.all()
        return ctx


class TeacherDetailView(LoginRequiredMixin, DetailView):
    model = TeacherProfile
    template_name = "teachers/detail.html"
    context_object_name = "teacher"

    def get_queryset(self):
        return (
            TeacherProfile.objects.filter(state=TeacherProfile.State.VALIDATED)
            .select_related("profile__user")
            .prefetch_related("subjects", "certificates")
        )


class TeacherProfileView(LoginRequiredMixin, View):
    template_name = "teachers/profile.html"

    def get(self, request):
        profile = request.user.profile
        if not profile.is_teacher:
            return redirect("profiles:profile")
        tp, _ = TeacherProfile.objects.get_or_create(profile=profile)
        return render(request, self.template_name, {"teacher_profile": tp})


class TeacherProfileEditView(LoginRequiredMixin, View):
    template_name = "teachers/profile_edit.html"

    def _get_tp(self, request):
        profile = request.user.profile
        if not profile.is_teacher:
            return None
        tp, _ = TeacherProfile.objects.get_or_create(profile=profile)
        return tp

    def get(self, request):
        tp = self._get_tp(request)
        if tp is None:
            return redirect("profiles:profile")
        form = TeacherProfileForm(instance=tp)
        cert_formset = CertificateFormSet(instance=tp)
        return render(request, self.template_name, {"form": form, "cert_formset": cert_formset, "teacher_profile": tp})

    def post(self, request):
        tp = self._get_tp(request)
        if tp is None:
            return redirect("profiles:profile")
        form = TeacherProfileForm(request.POST, instance=tp)
        cert_formset = CertificateFormSet(request.POST, request.FILES, instance=tp)
        if form.is_valid() and cert_formset.is_valid():
            form.save()
            cert_formset.save()
            return redirect("teachers:profile")
        return render(request, self.template_name, {"form": form, "cert_formset": cert_formset, "teacher_profile": tp})
