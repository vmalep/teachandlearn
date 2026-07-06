import urllib.request
import urllib.parse
import json as _json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import ListView, DetailView
from .forms import CertificateFormSet, ClassOfferingFormSet, TeacherProfileForm
from .models import TeacherProfile
from subjects.models import Subject


def _municipality_coords(name):
    """Return (lat, lng) for a Belgian municipality using Nominatim, cached 24 h."""
    key = f"muni_coords:{name}"
    cached = cache.get(key)
    if cached:
        return cached
    query = urllib.parse.urlencode({
        "q": f"{name}, Belgium",
        "format": "json",
        "limit": "1",
        "countrycodes": "be",
    })
    url = f"https://nominatim.openstreetmap.org/search?{query}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "TeachAndLearn/1.0"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            results = _json.loads(resp.read())
        if results:
            coords = (float(results[0]["lat"]), float(results[0]["lon"]))
            cache.set(key, coords, 86400)
            return coords
    except Exception:
        pass
    return None


def _rating_qs(qs):
    return qs.annotate(
        avg_rating=Avg(
            "profile__user__received_reviews__rating",
            filter=Q(profile__user__received_reviews__state="validated"),
        ),
        review_count=Count(
            "profile__user__received_reviews",
            filter=Q(profile__user__received_reviews__state="validated"),
        ),
    )


class TeacherDirectoryView(ListView):
    model = TeacherProfile
    template_name = "teachers/directory.html"
    context_object_name = "teachers"

    def get_queryset(self):
        qs = _rating_qs(
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
        return qs.order_by("-avg_rating", "price_per_hour")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["all_subjects"] = Subject.objects.all()
        return ctx


class TeacherDetailView(LoginRequiredMixin, DetailView):
    model = TeacherProfile
    template_name = "teachers/detail.html"
    context_object_name = "teacher"

    def get_queryset(self):
        return _rating_qs(
            TeacherProfile.objects.filter(state=TeacherProfile.State.VALIDATED)
            .select_related("profile__user")
            .prefetch_related("subjects", "certificates", "offerings__subject")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        teacher = self.object
        from reviews.models import Review
        ctx["reviews"] = Review.objects.filter(
            teacher=teacher.profile.user, state=Review.State.VALIDATED
        ).select_related("student").order_by("-created_at")

        ctx["offerings"] = teacher.offerings.filter(is_active=True)
        if self.request.user.is_authenticated:
            ctx["user_review"] = Review.objects.filter(
                student=self.request.user, teacher=teacher.profile.user
            ).first()
            from messaging.models import Conversation
            ctx["conversation"] = Conversation.objects.filter(
                student=self.request.user, teacher=teacher.profile.user
            ).first()
        return ctx


class MapView(View):
    def get(self, request):
        return render(request, "map.html", {"all_subjects": Subject.objects.all()})


class MapDataView(View):
    def get(self, request):
        from students.models import StudentProfile

        subject_id = request.GET.get("subject")

        teacher_qs = (
            TeacherProfile.objects
            .filter(state=TeacherProfile.State.VALIDATED)
            .filter(profile__municipality__gt="")
        )
        if subject_id:
            teacher_qs = teacher_qs.filter(subjects__id=subject_id)

        teacher_rows = (
            teacher_qs
            .values("profile__municipality")
            .annotate(count=Count("id", distinct=True))
        )

        student_qs = (
            StudentProfile.objects
            .filter(profile__municipality__gt="")
        )
        if subject_id:
            student_qs = student_qs.filter(subject_levels__subject__id=subject_id)

        student_rows = (
            student_qs
            .values("profile__municipality")
            .annotate(count=Count("id", distinct=True))
        )

        data = {}
        for row in teacher_rows:
            m = row["profile__municipality"]
            data[m] = {"municipality": m, "teachers": row["count"], "students": 0}
        for row in student_rows:
            m = row["profile__municipality"]
            if m in data:
                data[m]["students"] = row["count"]
            else:
                data[m] = {"municipality": m, "teachers": 0, "students": row["count"]}

        # Resolve each municipality to its centroid via Nominatim (cached)
        result = []
        for entry in data.values():
            coords = _municipality_coords(entry["municipality"])
            if coords:
                entry["lat"], entry["lng"] = coords
                result.append(entry)

        return JsonResponse(result, safe=False)


class TeacherProfileView(LoginRequiredMixin, View):
    template_name = "teachers/profile.html"

    def get(self, request):
        profile = request.user.profile
        if not profile.is_teacher:
            return redirect("profiles:profile")
        tp, _ = TeacherProfile.objects.get_or_create(profile=profile)
        return render(request, self.template_name, {
            "teacher_profile": tp,
            "offerings": tp.offerings.select_related("subject").all(),
        })


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
        offering_formset = ClassOfferingFormSet(instance=tp)
        return render(request, self.template_name, {
            "form": form,
            "cert_formset": cert_formset,
            "offering_formset": offering_formset,
            "teacher_profile": tp,
        })

    def post(self, request):
        tp = self._get_tp(request)
        if tp is None:
            return redirect("profiles:profile")
        form = TeacherProfileForm(request.POST, instance=tp)
        cert_formset = CertificateFormSet(request.POST, request.FILES, instance=tp)
        offering_formset = ClassOfferingFormSet(request.POST, instance=tp)
        if form.is_valid() and cert_formset.is_valid() and offering_formset.is_valid():
            form.save()
            cert_formset.save()
            offering_formset.save()
            return redirect("teachers:profile")
        return render(request, self.template_name, {
            "form": form,
            "cert_formset": cert_formset,
            "offering_formset": offering_formset,
            "teacher_profile": tp,
        })
