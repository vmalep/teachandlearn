from django.db.models import Q
from .models import Message


def unread_message_count(request):
    if not request.user.is_authenticated:
        return {}
    count = (
        Message.objects
        .filter(Q(conversation__student=request.user) | Q(conversation__teacher=request.user))
        .exclude(sender=request.user)
        .filter(is_read=False)
        .count()
    )
    return {"unread_message_count": count}
