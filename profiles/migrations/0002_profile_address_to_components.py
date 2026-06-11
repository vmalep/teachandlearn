from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("profiles", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(model_name="profile", name="address"),
        migrations.AddField(
            model_name="profile",
            name="postal_code",
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AddField(
            model_name="profile",
            name="street",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name="profile",
            name="house_number",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="profile",
            name="mailbox",
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
