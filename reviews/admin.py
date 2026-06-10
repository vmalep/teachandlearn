from django.contrib import admin
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

    @admin.action(description="Reject selected reviews")
    def reject_reviews(self, request, queryset):
        queryset.update(state=Review.State.REJECTED)
