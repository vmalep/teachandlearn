from django.db import models


class Subject(models.Model):

    class Category(models.TextChoices):
        LANGUAGES = "languages", "Languages"
        SCIENCES = "sciences", "Sciences"
        HUMANITIES = "humanities", "Humanities"
        ARTS = "arts", "Arts"
        SPORTS = "sports", "Sports"
        PROFESSIONAL = "professional", "Professional skills"

    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(
        max_length=50,
        choices=Category.choices,
        default=Category.LANGUAGES,
        blank=True,
    )

    class Meta:
        ordering = ["category", "name"]

    def __str__(self):
        return self.name
