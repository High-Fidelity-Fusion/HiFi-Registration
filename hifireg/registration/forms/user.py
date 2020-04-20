from django import forms
from django.contrib.auth.forms import AuthenticationForm as AuthenticationForm_
from django.contrib.auth.forms import UserCreationForm as UserCreationForm_
from django.contrib.auth.forms import UsernameField
from django.utils.translation import gettext_lazy as _

from registration.models import User

user_fields = ('first_name', 'last_name', 'personal_pronouns', 'city', 'severe_allergies')

# Custom UserCreationForm for our custom User
class UserCreationForm(UserCreationForm_):
    # Redefine password field without the default help_text
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )

    # Modify/extend fields shown for the user
    class Meta:
        model = User
        fields = ('email', 'password1', 'password2') + user_fields


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email',) + user_fields


# Override AuthenticationForm to use EmailInput widget for UsernameField
# username is actually the email address -- this translation happens in base class.
class AuthenticationForm(AuthenticationForm_):
    username = UsernameField(widget=forms.EmailInput(attrs={'autofocus': True}))
