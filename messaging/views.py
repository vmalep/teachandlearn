from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.db.models import OuterRef, Q, Subquery
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import ListView
from .models import Conversation, Message
from accounts.models import User


def _user_conversations(user):
    last_msg = Message.objects.filter(
        conversation=OuterRef("pk")
    ).order_by("-created_at")
    return (
        Conversation.objects.filter(Q(student=user) | Q(teacher=user))
        .select_related("student", "teacher",
                        "student__profile", "teacher__profile")
        .annotate(
            last_message_body=Subquery(last_msg.values("body")[:1]),
            last_message_at=Subquery(last_msg.values("created_at")[:1]),
        )
        .order_by("-last_message_at", "-updated_at")
    )


class ConversationListView(LoginRequiredMixin, ListView):
    template_name = "messaging/list.html"
    context_object_name = "conversations"

    def get_queryset(self):
        return _user_conversations(self.request.user)


class ConversationDetailView(LoginRequiredMixin, View):
    template_name = "messaging/detail.html"

    def _get_conversation(self, request, pk):
        user = request.user
        return get_object_or_404(
            Conversation.objects.select_related("student", "teacher")
            .prefetch_related("messages__sender"),
            Q(student=user) | Q(teacher=user),
            pk=pk,
        )

    def get(self, request, pk):
        conversation = self._get_conversation(request, pk)
        other = conversation.teacher if request.user == conversation.student else conversation.student
        # Mark incoming messages as read
        conversation.messages.exclude(sender=request.user).filter(is_read=False).update(is_read=True)

        prefill_message = ""
        offering_id = request.GET.get("offering")
        if offering_id:
            from teachers.models import ClassOffering
            offering = ClassOffering.objects.filter(
                pk=offering_id, teacher__profile__user=conversation.teacher
            ).select_related("subject").first()
            if offering:
                prefill_message = _("Hi, I'm interested in your %(subject)s — %(format)s class.") % {
                    "subject": offering.subject,
                    "format": offering.get_format_display(),
                }

        return render(request, self.template_name, {
            "conversation": conversation,
            "thread": conversation.messages.all(),
            "other": other,
            "prefill_message": prefill_message,
        })

    def post(self, request, pk):
        conversation = self._get_conversation(request, pk)
        body = request.POST.get("body", "").strip()
        if body:
            Message.objects.create(
                conversation=conversation, sender=request.user, body=body
            )
            if conversation.state == Conversation.State.NEW:
                conversation.state = Conversation.State.ONGOING
                conversation.save(update_fields=["state", "updated_at"])
            # Email notification to recipient
            recipient = conversation.teacher if request.user == conversation.student else conversation.student
            send_mail(
                subject="New message on TeachAndLearn",
                message=f"You have a new message from {request.user.email}.\n\nLog in to read it: https://teachandlearn.cloud/messages/{pk}/",
                from_email=None,
                recipient_list=[recipient.email],
                fail_silently=True,
            )
        return redirect("messaging:detail", pk=pk)


class StartConversationView(LoginRequiredMixin, View):
    def post(self, request, teacher_pk):
        teacher_user = get_object_or_404(
            User, pk=teacher_pk, profile__is_teacher=True
        )
        if teacher_user == request.user:
            return redirect("home")
        conversation, _created = Conversation.objects.get_or_create(
            student=request.user, teacher=teacher_user
        )
        url = reverse("messaging:detail", kwargs={"pk": conversation.pk})
        offering_id = request.POST.get("offering")
        if offering_id:
            url += f"?offering={offering_id}"
        return redirect(url)
