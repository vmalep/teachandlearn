from django.contrib import admin
from django.contrib.admin import helpers
from django.template.response import TemplateResponse
from .models import ClassOffering, TeacherProfile, Certificate


class CertificateInline(admin.TabularInline):
    model = Certificate
    extra = 0


class ClassOfferingInline(admin.TabularInline):
    model = ClassOffering
    extra = 0


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ["profile", "state", "price_per_hour", "created_at"]
    list_filter = ["state"]
    search_fields = ["profile__user__email"]
    filter_horizontal = ["subjects"]
    inlines = [CertificateInline, ClassOfferingInline]
    actions = ["validate_profiles", "reject_profiles"]

    @admin.action(description="Validate selected teacher profiles")
    def validate_profiles(self, request, queryset):
        queryset.update(state=TeacherProfile.State.VALIDATED)
        self.message_user(request, f"{queryset.count()} teacher profile(s) validated.")

    @admin.action(description="Reject selected teacher profiles")
    def reject_profiles(self, request, queryset):
        if "apply" in request.POST:
            reason = request.POST.get("rejection_reason", "")
            selected_ids = request.POST.getlist(helpers.ACTION_CHECKBOX_NAME)
            updated = TeacherProfile.objects.filter(pk__in=selected_ids).update(
                state=TeacherProfile.State.REJECTED,
                rejection_reason=reason,
            )
            self.message_user(request, f"{updated} teacher profile(s) rejected.")
            return None

        return TemplateResponse(request, "admin/reject_with_reason.html", {
            "title": "Reject teacher profiles",
            "description": f"You are about to reject {queryset.count()} teacher profile(s). Optionally enter a reason:",
            "queryset": queryset,
            "action_name": "reject_profiles",
            "action_checkbox_name": helpers.ACTION_CHECKBOX_NAME,
            "opts": self.model._meta,
        })
