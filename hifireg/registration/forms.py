from django import forms
from django.contrib.auth.forms import UserCreationForm as UserCreationForm_
from .models import User, Registration, CompCode
from .models.comp_code import CompCodeHelper
from django.core.exceptions import ValidationError

from django.contrib.auth.forms import AuthenticationForm as AuthenticationForm_
from django.contrib.auth import password_validation
from django.utils.translation import gettext_lazy as _


from .models import User, Registration

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['agree_to_coc','allergens_severe']

class RegCompCodeForm(forms.Form):
    code = forms.CharField(label='If you have a Comp Code for a free ticket, enter it here:', max_length=CompCodeHelper.CODE_LENGTH, required=False)

    def clean(self):
        code = self.cleaned_data.get('code')
        if code:
            if not CompCode.objects.filter(code=code).exists():
                raise ValidationError('That is not a valid comp code!')
            comp_code = CompCode.objects.get(code=code)
            if comp_code.max_uses <= comp_code.registration_set.count():
                raise ValidationError('That code is already expended.')
        return self.cleaned_data


# Custom UserCreationForm for our custom User
class UserCreationForm(UserCreationForm_):
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'input'}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'input'}),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'input'}),
            'first_name': forms.TextInput(attrs={'class': 'input'}),
            'last_name': forms.TextInput(attrs={'class': 'input'}),
        }


# TODO: there is some sort of magic happening such that this form actually works correctly
#       under the custom user model as long as I don't try to modify the username field.
#       It seems to balk when I set the username to something saying that it doesn't exist
#       How does it know to not use that field?
class AuthenticationForm(AuthenticationForm_):
    # username = UsernameField(widget=forms.EmailInput(attrs={'autofocus': True, 'class': 'input'}))
    # username = UsernameField(widget=forms.TextInput(attrs={'autofocus': True}))

    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'class': 'input'}),
    )

    # class Meta:
    #     widgets = {
    #         'email': forms.EmailInput(attrs={'class': 'input'}),
    #     }
