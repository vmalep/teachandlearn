from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from .forms import ReviewForm
from .models import Review
from accounts.models import User


def _teacher_detail_redirect(teacher):
    return redirect("teacher-detail", pk=teacher.profile.teacher_profile.pk)


class WriteReviewView(LoginRequiredMixin, View):
    template_name = "reviews/write.html"

    def _get_teacher(self, teacher_pk):
        return get_object_or_404(User, pk=teacher_pk, profile__is_teacher=True)

    def _check_guards(self, request, teacher):
        """Return a redirect if request should be denied, else None."""
        if not request.user.profile.is_student:
            return _teacher_detail_redirect(teacher)
        if request.user == teacher:
            return _teacher_detail_redirect(teacher)
        return None

    def get(self, request, teacher_pk):
        teacher = self._get_teacher(teacher_pk)
        guard = self._check_guards(request, teacher)
        if guard:
            return guard
        existing = Review.objects.filter(student=request.user, teacher=teacher).first()
        form = ReviewForm(instance=existing)
        return render(request, self.template_name, {
            "form": form,
            "teacher": teacher,
            "existing": existing,
        })

    def post(self, request, teacher_pk):
        teacher = self._get_teacher(teacher_pk)
        guard = self._check_guards(request, teacher)
        if guard:
            return guard
        existing = Review.objects.filter(student=request.user, teacher=teacher).first()
        form = ReviewForm(request.POST, instance=existing)
        if form.is_valid():
            review = form.save(commit=False)
            review.student = request.user
            review.teacher = teacher
            review.state = Review.State.DRAFT
            review.save()
            return _teacher_detail_redirect(teacher)
        return render(request, self.template_name, {
            "form": form,
            "teacher": teacher,
            "existing": existing,
        })
