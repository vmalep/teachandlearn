from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from .models import Conversation, Message
from accounts.models import User


class ConversationListView(LoginRequiredMixin, ListView):
    template_name = "messaging/list.html"
    context_object_name = "conversations"

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(
            student=user
        ) | Conversation.objects.filter(teacher=user)


class ConversationDetailView(LoginRequiredMixin, DetailView):
    model = Conversation
    template_name = "messaging/detail.html"
    context_object_name = "conversation"

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(student=user) | Conversation.objects.filter(teacher=user)

    def post(self, request, pk):
        conversation = self.get_object()
        body = request.POST.get("body", "").strip()
        if body:
            Message.objects.create(conversation=conversation, sender=request.user, body=body)
            if conversation.state == Conversation.State.NEW:
                conversation.state = Conversation.State.ONGOING
                conversation.save()
        return redirect("messaging:detail", pk=pk)


class StartConversationView(LoginRequiredMixin, View):
    def post(self, request, teacher_pk):
        teacher_user = get_object_or_404(User, pk=teacher_pk)
        conversation, _ = Conversation.objects.get_or_create(
            student=request.user, teacher=teacher_user
        )
        return redirect("messaging:detail", pk=conversation.pk)
