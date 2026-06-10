from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "is_teacher", "is_student", "municipality"]
    list_filter = ["is_teacher", "is_student"]
    search_fields = ["user__email", "municipality"]
    raw_id_fields = ["user"]
