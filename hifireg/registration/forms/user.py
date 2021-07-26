from django import forms
from django.contrib.auth.forms import AuthenticationForm as AuthenticationForm_
from django.contrib.auth.forms import UserCreationForm as UserCreationForm_
from django.contrib.auth.forms import PasswordChangeForm as PasswordChangeForm_
from django.contrib.auth.forms import SetPasswordForm as SetPasswordForm_
from django.contrib.auth.forms import UsernameField
from django.utils.translation import gettext_lazy as _

from registration.models import User


user_fields = ('first_name', 'last_name', 'personal_pronouns', 'city', 'severe_allergies', 'covid_vaccine_picture')


# Redefine password field without the default help_text
password_field = forms.CharField(
    label=_("Password"),
    strip=False,
    widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
)


# Custom UserCreationForm for our custom User
class UserCreationForm(UserCreationForm_):
    password1 = password_field

    # Modify/extend fields shown for the user
    class Meta:
        model = User
        fields = ('email', 'password1', 'password2') + user_fields


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email',) + user_fields


class PasswordChangeForm(PasswordChangeForm_):
    new_password1 = password_field


class SetPasswordForm(SetPasswordForm_):
    new_password1 = password_field


# Override AuthenticationForm to use EmailInput widget for UsernameField
# username is actually the email address -- this translation happens in base class.
class AuthenticationForm(AuthenticationForm_):
    username = UsernameField(widget=forms.EmailInput(attrs={'autofocus': True}))
