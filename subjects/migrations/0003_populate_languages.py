from django.db import migrations

LANGUAGES = [
    "Arabic",
    "Chinese (Mandarin)",
    "Dutch",
    "English",
    "French",
    "German",
    "Italian",
    "Japanese",
    "Portuguese",
    "Russian",
    "Spanish",
    "Turkish",
]


def populate_languages(apps, schema_editor):
    Subject = apps.get_model("subjects", "Subject")
    for name in LANGUAGES:
        Subject.objects.get_or_create(name=name, defaults={"category": "languages"})


def remove_languages(apps, schema_editor):
    Subject = apps.get_model("subjects", "Subject")
    Subject.objects.filter(name__in=LANGUAGES).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("subjects", "0002_add_category_to_subject"),
    ]

    operations = [
        migrations.RunPython(populate_languages, remove_languages),
    ]
