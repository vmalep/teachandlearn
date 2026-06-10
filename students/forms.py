from django import forms
from django.forms import inlineformset_factory
from .models import StudentProfile, StudentSubject
from profiles.forms import apply_input_class


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ["learning_goals"]
        widgets = {
            "learning_goals": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_input_class(self)


class StudentSubjectForm(forms.ModelForm):
    class Meta:
        model = StudentSubject
        fields = ["subject", "level"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_input_class(self)


StudentSubjectFormSet = inlineformset_factory(
    StudentProfile,
    StudentSubject,
    form=StudentSubjectForm,
    extra=1,
    can_delete=True,
)
