from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from .forms import ReviewForm
from .models import Review
from accounts.models import User


class WriteReviewView(LoginRequiredMixin, View):
    template_name = "reviews/write.html"

    def get(self, request, teacher_pk):
        teacher = get_object_or_404(User, pk=teacher_pk)
        existing = Review.objects.filter(student=request.user, teacher=teacher).first()
        form = ReviewForm(instance=existing)
        return render(request, self.template_name, {"form": form, "teacher": teacher})

    def post(self, request, teacher_pk):
        teacher = get_object_or_404(User, pk=teacher_pk)
        if request.user == teacher:
            return redirect("home")
        existing = Review.objects.filter(student=request.user, teacher=teacher).first()
        form = ReviewForm(request.POST, instance=existing)
        if form.is_valid():
            review = form.save(commit=False)
            review.student = request.user
            review.teacher = teacher
            review.state = Review.State.DRAFT
            review.save()
            return redirect("teacher-detail", pk=teacher.profile.teacher_profile.pk)
        return render(request, self.template_name, {"form": form, "teacher": teacher})
