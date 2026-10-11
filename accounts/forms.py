from django import forms
from django.contrib.auth.forms import SetPasswordForm, UserCreationForm
from django.db import transaction

from .models import User


PASSWORD_HELP = (
    "<ul class='pw-rules'>"
    "<li>At least 8 characters</li>"
    "<li>Avoid common passwords like <i>password123</i></li>"
    "<li>Can't be all numbers</li>"
    "</ul>"
)


class CampusSetPasswordForm(SetPasswordForm):
    """Used on the reset-password page."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["new_password1"].help_text = PASSWORD_HELP


class RegisterForm(UserCreationForm):
    ROLE_CHOICES = [(User.Role.STUDENT, "Student"), (User.Role.RECRUITER, "Recruiter")]
    role = forms.ChoiceField(choices=ROLE_CHOICES, initial=User.Role.STUDENT)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "role")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].help_text = PASSWORD_HELP

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit and user.role == User.Role.STUDENT:
            from students.models import StudentProfile
            StudentProfile.objects.get_or_create(user=user, defaults={"full_name": user.username})
        return user
