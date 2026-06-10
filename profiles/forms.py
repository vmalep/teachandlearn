from django import forms
from .models import Profile


def apply_input_class(form):
    skip = (forms.CheckboxInput, forms.CheckboxSelectMultiple, forms.RadioSelect)
    for field in form.fields.values():
        if not isinstance(field.widget, skip):
            field.widget.attrs.setdefault("class", "field-input")


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["bio", "avatar", "municipality", "address", "is_teacher", "is_student"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
            "address": forms.TextInput(),
        }
        labels = {
            "address": "Full address (private — used for map only)",
            "is_teacher": "I want to teach",
            "is_student": "I want to learn",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_input_class(self)
