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
        fields = [
            "bio", "avatar",
            "postal_code", "municipality", "street", "house_number", "mailbox",
            "is_teacher", "is_student",
        ]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
            "postal_code": forms.TextInput(attrs={
                "maxlength": "4",
                "inputmode": "numeric",
                "autocomplete": "postal-code",
                "pattern": "[0-9]{4}",
                "hx-get": "/profiles/municipalities/",
                "hx-trigger": "input changed delay:600ms",
                "hx-target": "#municipality-wrapper",
            }),
        }
        labels = {
            "postal_code": "Postal code",
            "street": "Street",
            "house_number": "Number",
            "mailbox": "Mailbox",
            "is_teacher": "I want to teach",
            "is_student": "I want to learn",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["postal_code"].required = True
        self.fields["municipality"].required = True
        apply_input_class(self)
