import urllib.request
import urllib.parse
import json as _json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.db.models import Avg, Count, F, FloatField, Q, Value
from django.db.models.functions import ACos, Cast, Cos, Greatest, Least, Radians, Sin
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import ListView, DetailView
from .forms import CertificateFormSet, ClassOfferingFormSet, TeacherPresentationForm, TeacherProfileForm
from .models import ClassOffering, TeacherProfile, TeachingMode
from subjects.models import Subject

EARTH_RADIUS_KM = 6371.0


def _geocode_text(text):
    """Return (lat, lng) for a free-text location (municipality or address) via Nominatim, cached 24 h."""
    key = f"geocode_text:{text}"
    cached = cache.get(key)
    if cached:
        return cached
    query = urllib.parse.urlencode({
        "q": f"{text}, Belgium",
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


def _annotate_distance_km(qs, lat, lng, lat_field="profile__latitude", lng_field="profile__longitude"):
    """Annotate queryset with great-circle distance (km) from (lat, lng) to the given lat/lng fields."""
    lat_rad = Radians(Value(lat, output_field=FloatField()))
    lng_rad = Radians(Value(lng, output_field=FloatField()))
    target_lat_rad = Radians(Cast(lat_field, FloatField()))
    target_lng_rad = Radians(Cast(lng_field, FloatField()))
    cos_angle = (
        Cos(lat_rad) * Cos(target_lat_rad) * Cos(target_lng_rad - lng_rad)
        + Sin(lat_rad) * Sin(target_lat_rad)
    )
    # Clamp to [-1, 1] — floating-point rounding can push it just outside that
    # range for near-identical points, which would make ACos raise in Postgres.
    clamped = Least(Value(1.0), Greatest(Value(-1.0), cos_angle))
    return qs.annotate(distance_km=ACos(clamped) * EARTH_RADIUS_KM)


def _rating_qs(qs, prefix="profile__user__received_reviews"):
    return qs.annotate(
        avg_rating=Avg(
            f"{prefix}__rating",
            filter=Q(**{f"{prefix}__state": "validated"}),
        ),
        review_count=Count(
            prefix,
            filter=Q(**{f"{prefix}__state": "validated"}),
        ),
    )


class TeacherDirectoryView(ListView):
    model = ClassOffering
    template_name = "teachers/directory.html"
    context_object_name = "offerings"

    def get_queryset(self):
        qs = _rating_qs(
            ClassOffering.objects.filter(
                is_active=True,
                teacher__state=TeacherProfile.State.VALIDATED,
            )
            .select_related("subject", "teacher__profile__user"),
            prefix="teacher__profile__user__received_reviews",
        )
        subject = self.request.GET.get("subject")
        municipality = self.request.GET.get("municipality")
        max_price = self.request.GET.get("max_price")
        near = self.request.GET.get("near", "").strip()
        radius_km = self.request.GET.get("radius_km")
        teaching_mode = self.request.GET.get("teaching_mode")
        format_ = self.request.GET.get("format")
        sort = self.request.GET.get("sort", "rating")

        if subject:
            qs = qs.filter(subject__id=subject)
        if teaching_mode:
            qs = qs.filter(teaching_mode=teaching_mode)
        if format_:
            qs = qs.filter(format=format_)
        if max_price:
            try:
                qs = qs.filter(price_per_hour__lte=float(max_price))
            except ValueError:
                pass

        ref_point = None
        self.near_error = False
        if near:
            coords = _geocode_text(near)
            if coords:
                ref_point = coords
            else:
                self.near_error = True
                qs = qs.none()
        elif municipality:
            qs = qs.filter(teacher__profile__municipality=municipality)

        distance_annotated = False
        if ref_point and radius_km and not self.near_error:
            try:
                radius = float(radius_km)
            except ValueError:
                radius = None
            if radius:
                lat, lng = ref_point
                qs = _annotate_distance_km(
                    qs, lat, lng,
                    lat_field="teacher__profile__latitude",
                    lng_field="teacher__profile__longitude",
                ).filter(
                    teacher__profile__latitude__isnull=False,
                    teacher__profile__longitude__isnull=False,
                    distance_km__lte=radius,
                )
                distance_annotated = True

        self.sort_unavailable = False
        if sort == "distance":
            if not ref_point and self.request.user.is_authenticated:
                profile = getattr(self.request.user, "profile", None)
                if profile and profile.latitude is not None and profile.longitude is not None:
                    ref_point = (float(profile.latitude), float(profile.longitude))
            if ref_point and not self.near_error:
                if not distance_annotated:
                    lat, lng = ref_point
                    qs = _annotate_distance_km(
                        qs, lat, lng,
                        lat_field="teacher__profile__latitude",
                        lng_field="teacher__profile__longitude",
                    )
                return qs.order_by(F("distance_km").asc(nulls_last=True), "-avg_rating")
            self.sort_unavailable = True

        if sort == "price":
            return qs.order_by("price_per_hour", "-avg_rating")

        return qs.order_by("-avg_rating", "price_per_hour")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["all_subjects"] = (
            Subject.objects.filter(
                classoffering__is_active=True,
                classoffering__teacher__state=TeacherProfile.State.VALIDATED,
            )
            .order_by("name")
            .distinct()
        )
        ctx["teaching_mode_choices"] = TeachingMode.choices
        ctx["format_choices"] = ClassOffering.Format.choices
        ctx["all_municipalities"] = (
            TeacherProfile.objects.filter(state=TeacherProfile.State.VALIDATED)
            .exclude(profile__municipality="")
            .order_by("profile__municipality")
            .values_list("profile__municipality", flat=True)
            .distinct()
        )
        ctx["near_error"] = getattr(self, "near_error", False)
        ctx["sort_unavailable"] = getattr(self, "sort_unavailable", False)
        return ctx


class TeacherDetailView(LoginRequiredMixin, DetailView):
    model = TeacherProfile
    template_name = "teachers/detail.html"
    context_object_name = "teacher"

    def get_queryset(self):
        return _rating_qs(
            TeacherProfile.objects.filter(state=TeacherProfile.State.VALIDATED)
            .select_related("profile__user")
            .prefetch_related("certificates", "offerings__subject")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        teacher = self.object
        ctx["offerings"] = teacher.offerings.filter(is_active=True).select_related("subject")
        from reviews.models import Review
        ctx["reviews"] = Review.objects.filter(
            teacher=teacher.profile.user, state=Review.State.VALIDATED
        ).select_related("student").order_by("-created_at")

        if self.request.user.is_authenticated:
            ctx["user_review"] = Review.objects.filter(
                student=self.request.user, teacher=teacher.profile.user
            ).first()
            from messaging.models import Conversation
            ctx["conversation"] = Conversation.objects.filter(
                student=self.request.user, teacher=teacher.profile.user
            ).first()
        return ctx


class OfferingDetailView(LoginRequiredMixin, DetailView):
    model = ClassOffering
    template_name = "teachers/offering_detail.html"
    context_object_name = "offering"

    def get_queryset(self):
        return _rating_qs(
            ClassOffering.objects.filter(
                is_active=True,
                teacher__state=TeacherProfile.State.VALIDATED,
                teacher__pk=self.kwargs["teacher_pk"],
            )
            .select_related("subject", "teacher__profile__user"),
            prefix="teacher__profile__user__received_reviews",
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        offering = self.object
        teacher = offering.teacher
        ctx["teacher"] = teacher
        if self.request.user.is_authenticated:
            from messaging.models import Conversation
            ctx["conversation"] = Conversation.objects.filter(
                student=self.request.user, teacher=teacher.profile.user
            ).first()
        return ctx


class MapView(View):
    def get(self, request):
        all_subjects = (
            Subject.objects.filter(
                classoffering__is_active=True,
                classoffering__teacher__state=TeacherProfile.State.VALIDATED,
            )
            .order_by("name")
            .distinct()
        )
        return render(request, "map.html", {"all_subjects": all_subjects})


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
            teacher_qs = teacher_qs.filter(
                offerings__is_active=True, offerings__subject__id=subject_id
            )

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
            coords = _geocode_text(entry["municipality"])
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
        presentation_form = TeacherPresentationForm(instance=tp.profile)
        form = TeacherProfileForm(instance=tp)
        cert_formset = CertificateFormSet(instance=tp)
        offering_formset = ClassOfferingFormSet(instance=tp)
        return render(request, self.template_name, {
            "presentation_form": presentation_form,
            "form": form,
            "cert_formset": cert_formset,
            "offering_formset": offering_formset,
            "teacher_profile": tp,
        })

    def post(self, request):
        tp = self._get_tp(request)
        if tp is None:
            return redirect("profiles:profile")
        presentation_form = TeacherPresentationForm(request.POST, instance=tp.profile)
        form = TeacherProfileForm(request.POST, instance=tp)
        cert_formset = CertificateFormSet(request.POST, request.FILES, instance=tp)
        offering_formset = ClassOfferingFormSet(request.POST, instance=tp)
        if presentation_form.is_valid() and form.is_valid() and cert_formset.is_valid() and offering_formset.is_valid():
            presentation_form.save()
            form.save()
            cert_formset.save()
            offering_formset.save()
            return redirect("teachers:profile")
        return render(request, self.template_name, {
            "presentation_form": presentation_form,
            "form": form,
            "cert_formset": cert_formset,
            "offering_formset": offering_formset,
            "teacher_profile": tp,
        })
