from django.db import models


class StudentProfile(models.Model):
    class Level(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        ELEMENTARY = "elementary", "Elementary"
        INTERMEDIATE = "intermediate", "Intermediate"
        UPPER_INTERMEDIATE = "upper_intermediate", "Upper Intermediate"
        ADVANCED = "advanced", "Advanced"
        NATIVE = "native", "Native"

    profile = models.OneToOneField(
        "profiles.Profile", on_delete=models.CASCADE, related_name="student_profile"
    )
    learning_goals = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"StudentProfile({self.profile.user.email})"


class StudentSubject(models.Model):
    student = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE, related_name="subject_levels"
    )
    subject = models.ForeignKey(
        "subjects.Subject", on_delete=models.CASCADE
    )
    level = models.CharField(
        max_length=30, choices=StudentProfile.Level.choices, default=StudentProfile.Level.BEGINNER
    )

    class Meta:
        unique_together = ("student", "subject")

    def __str__(self):
        return f"{self.student.profile.user.email} — {self.subject} ({self.level})"
