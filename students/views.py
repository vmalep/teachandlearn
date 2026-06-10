from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View
from .forms import StudentProfileForm, StudentSubjectFormSet
from .models import StudentProfile


class StudentProfileView(LoginRequiredMixin, View):
    template_name = "students/profile.html"

    def get(self, request):
        profile = request.user.profile
        if not profile.is_student:
            return redirect("profiles:profile")
        sp, _ = StudentProfile.objects.get_or_create(profile=profile)
        return render(request, self.template_name, {"student_profile": sp})


class StudentProfileEditView(LoginRequiredMixin, View):
    template_name = "students/profile_edit.html"

    def _get_sp(self, request):
        profile = request.user.profile
        if not profile.is_student:
            return None
        sp, _ = StudentProfile.objects.get_or_create(profile=profile)
        return sp

    def get(self, request):
        sp = self._get_sp(request)
        if sp is None:
            return redirect("profiles:profile")
        form = StudentProfileForm(instance=sp)
        subj_formset = StudentSubjectFormSet(instance=sp)
        return render(request, self.template_name, {"form": form, "subj_formset": subj_formset})

    def post(self, request):
        sp = self._get_sp(request)
        if sp is None:
            return redirect("profiles:profile")
        form = StudentProfileForm(request.POST, instance=sp)
        subj_formset = StudentSubjectFormSet(request.POST, instance=sp)
        if form.is_valid() and subj_formset.is_valid():
            form.save()
            subj_formset.save()
            return redirect("students:profile")
        return render(request, self.template_name, {"form": form, "subj_formset": subj_formset})
