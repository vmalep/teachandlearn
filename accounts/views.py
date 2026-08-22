from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from .forms import RegisterForm
from .models import User


class RegisterView(View):
    template_name = "accounts/register.html"

    def get(self, request):
        return render(request, self.template_name, {"form": RegisterForm()})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            self._send_verification_email(request, user)
            return render(request, "accounts/register_done.html")
        return render(request, self.template_name, {"form": form})

    def _send_verification_email(self, request, user):
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        link = request.build_absolute_uri(f"/accounts/verify/{uid}/{token}/")
        send_mail(
            "Verify your TeachAndLearn account",
            f"Click the link to verify your email:\n\n{link}",
            None,
            [user.email],
        )


class VerifyEmailView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError):
            return render(request, "accounts/verify_invalid.html")

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.email_verified = True
            user.save()
            self._notify_admin_new_user(request, user)
            login(request, user)
            return redirect("/")
        return render(request, "accounts/verify_invalid.html")

    def _notify_admin_new_user(self, request, user):
        link = request.build_absolute_uri(f"/admin/accounts/user/{user.pk}/change/")
        send_mail(
            "New TeachAndLearn account verified",
            f"{user.get_full_name() or user.email} ({user.email}) just verified their account.\n\n{link}",
            None,
            [settings.ADMIN_NOTIFICATION_EMAIL],
        )
