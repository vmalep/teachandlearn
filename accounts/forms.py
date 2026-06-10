from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User

INPUT_CLASS = "field-input"


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Email"
        self.fields["username"].widget = forms.EmailInput(attrs={"class": INPUT_CLASS, "autofocus": True})
        self.fields["password"].widget.attrs["class"] = INPUT_CLASS


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", INPUT_CLASS)
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
