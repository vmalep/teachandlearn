from django.contrib import admin
from .models import TeacherProfile, Certificate


class CertificateInline(admin.TabularInline):
    model = Certificate
    extra = 0


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ["profile", "state", "price_per_hour", "created_at"]
    list_filter = ["state"]
    search_fields = ["profile__user__email"]
    filter_horizontal = ["subjects"]
    inlines = [CertificateInline]
    actions = ["validate_profiles", "reject_profiles"]

    @admin.action(description="Validate selected teacher profiles")
    def validate_profiles(self, request, queryset):
        queryset.update(state=TeacherProfile.State.VALIDATED)

    @admin.action(description="Reject selected teacher profiles")
    def reject_profiles(self, request, queryset):
        queryset.update(state=TeacherProfile.State.REJECTED)
