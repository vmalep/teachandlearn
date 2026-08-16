import urllib.parse
import urllib.request

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from profiles.models import Profile

# DiceBear "micah" — illustrated portrait avatars, deterministic per seed.
# Public API, no key required: https://www.dicebear.com/styles/micah/
DICEBEAR_URL = "https://api.dicebear.com/9.x/micah/png"
BACKGROUND_COLORS = "f5e9da,dceee0,e0e7ff,fde8e8,fef3c7"
_UA = "TeachAndLearn/1.0"


class Command(BaseCommand):
    help = "Generate mock avatar images (DiceBear illustrated portraits) for profiles without one."

    def add_arguments(self, parser):
        parser.add_argument(
            "--overwrite", action="store_true",
            help="Regenerate avatars even for profiles that already have one.",
        )

    def handle(self, *args, **options):
        qs = Profile.objects.select_related("user").all()
        if not options["overwrite"]:
            qs = qs.filter(avatar="")

        count = 0
        for profile in qs:
            query = urllib.parse.urlencode({
                "seed": profile.user.email,
                "size": "256",
                "backgroundColor": BACKGROUND_COLORS,
            })
            url = f"{DICEBEAR_URL}?{query}"
            try:
                req = urllib.request.Request(url, headers={"User-Agent": _UA})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    data = resp.read()
            except Exception as e:
                self.stdout.write(f"  failed {profile.user.email}: {e}")
                continue

            if profile.avatar:
                profile.avatar.delete(save=False)
            profile.avatar.save(f"{profile.user.pk}.png", ContentFile(data), save=True)
            count += 1
            self.stdout.write(f"  generated avatar for {profile.user.email}")

        self.stdout.write(self.style.SUCCESS(f"\nDone: {count} avatar(s) generated."))
