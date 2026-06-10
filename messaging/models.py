from django.conf import settings
from django.db import models


class Conversation(models.Model):
    class State(models.TextChoices):
        NEW = "new", "New"
        ONGOING = "ongoing", "Ongoing"
        CLOSED = "closed", "Closed"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_conversations",
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="teacher_conversations",
    )
    state = models.CharField(max_length=20, choices=State.choices, default=State.NEW)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "teacher")

    def __str__(self):
        return f"Conversation({self.student.email} → {self.teacher.email})"


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages",
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Message({self.sender.email}, {self.created_at:%Y-%m-%d %H:%M})"
