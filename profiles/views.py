import json
import os
import urllib.parse
import urllib.request
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, UpdateView
from .forms import ProfileForm
from .models import Profile

_UA = "TeachAndLearn/1.0 vmalep@pm.me"
_POSTAL_FILE = os.path.join(os.path.dirname(__file__), "postal_codes_be.json")

with open(_POSTAL_FILE, encoding="utf-8") as _f:
    _POSTAL_DATA = json.load(_f)


def _fetch_municipalities(postal_code):
    """Return sorted list of locality names for a Belgian postal code.

    Merges official municipality names (static JSON from statbel) with
    sub-localities returned by Overpass (e.g. Jambes for 5100).
    """
    seen = set()
    results = []

    # 1. Overpass — place nodes tagged with postal_code (sub-localities)
    try:
        overpass_query = (
            '[out:json][timeout:10];'
            'area["ISO3166-1:alpha2"="BE"]->.be;'
            f'(node["place"]["postal_code"="{postal_code}"](area.be);'
            f'node["place"]["addr:postcode"="{postal_code}"](area.be););'
            'out tags;'
        )
        req = urllib.request.Request(
            "https://overpass-api.de/api/interpreter",
            data=overpass_query.encode(),
            headers={"User-Agent": _UA},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            elements = json.loads(resp.read()).get("elements", [])
        for e in elements:
            name = e.get("tags", {}).get("name", "").strip()
            if name and name not in seen:
                seen.add(name)
                results.append(name)
    except Exception:
        pass

    # 2. Static file — official municipality names (always available)
    for name in _POSTAL_DATA.get(postal_code, []):
        if name not in seen:
            seen.add(name)
            results.append(name)

    return sorted(results)


def _geocode_profile(profile):
    """Geocode a profile's address via Nominatim. Updates lat/lon in place (no save)."""
    parts = []
    if profile.street:
        street = f"{profile.house_number} {profile.street}".strip() if profile.house_number else profile.street
        parts.append(street)
    # Strip bilingual suffix e.g. "Namur / Namen" → "Namur"
    municipality = profile.municipality.split("/")[0].strip() if profile.municipality else ""
    if profile.postal_code:
        parts.append(profile.postal_code)
    if municipality:
        parts.append(municipality)
    parts.append("Belgium")

    params = urllib.parse.urlencode({"q": ", ".join(parts), "format": "json", "limit": "1"})
    req = urllib.request.Request(
        f"https://nominatim.openstreetmap.org/search?{params}",
        headers={"User-Agent": _UA},
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            results = json.loads(resp.read())
        if results:
            profile.latitude = results[0]["lat"]
            profile.longitude = results[0]["lon"]
        else:
            profile.latitude = None
            profile.longitude = None
    except Exception:
        pass  # keep existing coordinates if geocoding fails


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
        profile = form.save(commit=False)
        _geocode_profile(profile)
        profile.save()
        form.save_m2m()
        if profile.is_teacher:
            from teachers.models import TeacherProfile
            TeacherProfile.objects.get_or_create(profile=profile)
        if profile.is_student:
            from students.models import StudentProfile
            StudentProfile.objects.get_or_create(profile=profile)
        return redirect(self.success_url)


class MunicipalityLookupView(LoginRequiredMixin, View):
    def get(self, request):
        postal_code = request.GET.get("postal_code", "").strip()
        municipalities = []
        error = False

        if len(postal_code) == 4 and postal_code.isdigit():
            try:
                municipalities = _fetch_municipalities(postal_code)
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
