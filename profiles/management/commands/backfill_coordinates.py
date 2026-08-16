import time

from django.core.management.base import BaseCommand

from profiles.models import Profile
from profiles.views import _geocode_profile


class Command(BaseCommand):
    help = "Geocode profiles that have an address but no latitude/longitude yet."

    def handle(self, *args, **options):
        profiles = Profile.objects.filter(latitude__isnull=True).exclude(municipality="")
        total = profiles.count()
        if not total:
            self.stdout.write("Nothing to do — all profiles already geocoded.")
            return

        updated = 0
        for i, profile in enumerate(profiles, start=1):
            _geocode_profile(profile)
            if profile.latitude and profile.longitude:
                profile.save(update_fields=["latitude", "longitude"])
                updated += 1
                self.stdout.write(f"  [{i}/{total}] geocoded {profile.user.email}")
            else:
                self.stdout.write(f"  [{i}/{total}] failed {profile.user.email}")
            # Nominatim usage policy: max 1 request/second.
            if i < total:
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS(f"\nDone: {updated}/{total} geocoded."))
