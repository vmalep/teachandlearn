import json
import urllib.request
import urllib.parse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import View
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


class MunicipalityLookupView(LoginRequiredMixin, View):
    def get(self, request):
        postal_code = request.GET.get("postal_code", "").strip()
        municipalities = []
        error = False

        if len(postal_code) == 4 and postal_code.isdigit():
            try:
                params = urllib.parse.urlencode({
                    "postalcode": postal_code,
                    "countrycodes": "be",
                    "format": "json",
                    "addressdetails": "1",
                    "limit": "50",
                })
                url = f"https://nominatim.openstreetmap.org/search?{params}"
                req = urllib.request.Request(
                    url, headers={"User-Agent": "TeachAndLearn/1.0 vmalep@pm.me"}
                )
                with urllib.request.urlopen(req, timeout=5) as resp:
                    results = json.loads(resp.read())

                # Keep only place/boundary features; use their own name (not parent city)
                locality_classes = {
                    ("place", "city"), ("place", "town"), ("place", "village"),
                    ("place", "suburb"), ("place", "quarter"), ("place", "hamlet"),
                    ("place", "neighbourhood"), ("place", "borough"),
                    ("boundary", "administrative"),
                }
                seen = set()
                for r in results:
                    key = (r.get("class", ""), r.get("type", ""))
                    if key not in locality_classes:
                        continue
                    name = r.get("name", "").strip()
                    if name and name not in seen:
                        seen.add(name)
                        municipalities.append(name)
                municipalities.sort()
            except Exception:
                error = True

        html = render_to_string(
            "profiles/municipality_options.html",
            {
                "municipalities": municipalities,
                "error": error,
                "postal_code": postal_code,
            },
            request=request,
        )
        return HttpResponse(html)
