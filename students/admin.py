from django.contrib import admin
from .models import StudentProfile, StudentSubject


class StudentSubjectInline(admin.TabularInline):
    model = StudentSubject
    extra = 0


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ["profile"]
    search_fields = ["profile__user__email"]
    inlines = [StudentSubjectInline]
