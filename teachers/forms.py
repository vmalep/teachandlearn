from django import forms
from django.forms import inlineformset_factory
from .models import Certificate, TeacherProfile
from .widgets import AvailabilityWidget
from profiles.forms import apply_input_class


class AvailabilityScheduleField(forms.Field):
    widget = AvailabilityWidget

    def to_python(self, value):
        return value if isinstance(value, dict) else {}

    def has_changed(self, initial, data):
        return (initial or {}) != (data or {})


class TeacherProfileForm(forms.ModelForm):
    availability_schedule = AvailabilityScheduleField(required=False)

    class Meta:
        model = TeacherProfile
        fields = ["subjects", "native_language", "price_per_hour", "teaching_mode", "availability", "availability_schedule"]
        widgets = {
            "subjects": forms.CheckboxSelectMultiple(),
            "availability": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_input_class(self)


class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ["name", "issuing_org", "date_obtained", "date_expiry", "file"]
        widgets = {
            "date_obtained": forms.DateInput(attrs={"type": "date"}),
            "date_expiry": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_input_class(self)


CertificateFormSet = inlineformset_factory(
    TeacherProfile,
    Certificate,
    form=CertificateForm,
    extra=1,
    can_delete=True,
)
