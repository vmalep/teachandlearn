from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TeacherProfile


@receiver(post_save, sender=TeacherProfile)
def notify_admin_new_teacher(sender, instance, created, **kwargs):
    if not created:
        return
    user = instance.profile.user
    link = f"{settings.SITE_URL}/admin/teachers/teacherprofile/{instance.pk}/change/"
    send_mail(
        "New teacher profile awaiting validation",
        f"{user.get_full_name() or user.email} ({user.email}) created a teacher profile "
        f"and is waiting for validation.\n\n{link}",
        None,
        [settings.ADMIN_NOTIFICATION_EMAIL],
    )
