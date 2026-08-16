import hashlib
import io

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw, ImageFont

from profiles.models import Profile

PALETTE = [
    "#7c3aed", "#0891b2", "#059669", "#d97706",
    "#dc2626", "#db2777", "#4f46e5", "#0d9488",
]


class Command(BaseCommand):
    help = "Generate simple placeholder avatar images (colored initial) for profiles without one."

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
        font = ImageFont.load_default(size=120)
        for profile in qs:
            initial = (profile.user.first_name or profile.user.email)[0].upper()
            color = PALETTE[
                int(hashlib.md5(profile.user.email.encode()).hexdigest(), 16) % len(PALETTE)
            ]

            img = Image.new("RGB", (256, 256), color)
            draw = ImageDraw.Draw(img)
            bbox = draw.textbbox((0, 0), initial, font=font)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text(
                ((256 - w) / 2 - bbox[0], (256 - h) / 2 - bbox[1]),
                initial, fill="white", font=font,
            )

            buf = io.BytesIO()
            img.save(buf, format="PNG")
            profile.avatar.save(
                f"{profile.user.pk}.png", ContentFile(buf.getvalue()), save=True
            )
            count += 1
            self.stdout.write(f"  generated avatar for {profile.user.email}")

        self.stdout.write(self.style.SUCCESS(f"\nDone: {count} avatar(s) generated."))
