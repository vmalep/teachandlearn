from django.contrib import admin
from .models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ["sender", "body", "created_at"]


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ["student", "teacher", "state", "created_at"]
    list_filter = ["state"]
    search_fields = ["student__email", "teacher__email"]
    inlines = [MessageInline]
