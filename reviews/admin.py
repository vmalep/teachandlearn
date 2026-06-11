from django.contrib import admin
from django.contrib.admin import helpers
from django.template.response import TemplateResponse
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["student", "teacher", "rating", "state", "created_at"]
    list_filter = ["state", "rating"]
    search_fields = ["student__email", "teacher__email"]
    actions = ["validate_reviews", "reject_reviews"]

    @admin.action(description="Validate selected reviews")
    def validate_reviews(self, request, queryset):
        queryset.update(state=Review.State.VALIDATED)
        self.message_user(request, f"{queryset.count()} review(s) validated.")

    @admin.action(description="Reject selected reviews")
    def reject_reviews(self, request, queryset):
        if "apply" in request.POST:
            reason = request.POST.get("rejection_reason", "")
            selected_ids = request.POST.getlist(helpers.ACTION_CHECKBOX_NAME)
            updated = Review.objects.filter(pk__in=selected_ids).update(
                state=Review.State.REJECTED,
                rejection_reason=reason,
            )
            self.message_user(request, f"{updated} review(s) rejected.")
            return None

        return TemplateResponse(request, "admin/reject_with_reason.html", {
            "title": "Reject reviews",
            "description": f"You are about to reject {queryset.count()} review(s). Optionally enter a reason:",
            "queryset": queryset,
            "action_name": "reject_reviews",
            "action_checkbox_name": helpers.ACTION_CHECKBOX_NAME,
            "opts": self.model._meta,
        })
