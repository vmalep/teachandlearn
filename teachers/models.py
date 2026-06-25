from django.db import models
from django.core.validators import MinValueValidator


class TeacherProfile(models.Model):
    class State(models.TextChoices):
        DRAFT = "draft", "Draft"
        VALIDATED = "validated", "Validated"
        REJECTED = "rejected", "Rejected"

    class TeachingMode(models.TextChoices):
        ONLINE = "online", "Online"
        PRESENTIAL = "presential", "Presential"
        BOTH = "both", "Both"

    profile = models.OneToOneField(
        "profiles.Profile", on_delete=models.CASCADE, related_name="teacher_profile"
    )
    subjects = models.ManyToManyField("subjects.Subject", blank=True)
    native_language = models.CharField(max_length=100, blank=True)
    price_per_hour = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    teaching_mode = models.CharField(
        max_length=20, choices=TeachingMode.choices, default=TeachingMode.BOTH
    )
    availability = models.TextField(blank=True)
    state = models.CharField(max_length=20, choices=State.choices, default=State.DRAFT)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"TeacherProfile({self.profile.user.email})"

    @property
    def average_rating(self):
        reviews = self.profile.user.received_reviews.filter(state="validated")
        if not reviews.exists():
            return None
        return reviews.aggregate(models.Avg("rating"))["rating__avg"]


class Certificate(models.Model):
    teacher = models.ForeignKey(
        TeacherProfile, on_delete=models.CASCADE, related_name="certificates"
    )
    name = models.CharField(max_length=200)
    issuing_org = models.CharField(max_length=200, blank=True)
    date_obtained = models.DateField(null=True, blank=True)
    date_expiry = models.DateField(null=True, blank=True)
    file = models.FileField(upload_to="certificates/", blank=True)

    def __str__(self):
        return f"{self.name} — {self.teacher.profile.user.email}"
