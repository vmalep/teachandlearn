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

_UA = "TeachAndLearn/1.0 vmalep@pm.me"


def _fetch_municipalities(postal_code):
    """Return sorted list of locality names for a Belgian postal code.

    Tries Overpass first (good for sub-localities); falls back to Nominatim
    when Overpass returns nothing (e.g. large cities like Brussels).
    """
    # 1. Overpass — place nodes tagged with postal_code
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

    seen = set()
    results = []
    for e in elements:
        name = e.get("tags", {}).get("name", "").strip()
        if name and name not in seen:
            seen.add(name)
            results.append(name)

    if results:
        return sorted(results)

    # 2. Nominatim fallback — extracts city from the postal code boundary
    params = urllib.parse.urlencode({
        "postalcode": postal_code,
        "countrycodes": "be",
        "format": "json",
        "addressdetails": "1",
        "limit": "5",
    })
    req = urllib.request.Request(
        f"https://nominatim.openstreetmap.org/search?{params}",
        headers={"User-Agent": _UA},
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        nom_results = json.loads(resp.read())

    for r in nom_results:
        addr = r.get("address", {})
        name = (
            addr.get("city")
            or addr.get("town")
            or addr.get("village")
            or addr.get("municipality")
        )
        if name and name not in seen:
            seen.add(name)
            results.append(name)

    return sorted(results)


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
