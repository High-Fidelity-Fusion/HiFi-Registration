from django import forms
from django.contrib.auth.forms import AuthenticationForm as AuthenticationForm_
from django.contrib.auth.forms import UserCreationForm as UserCreationForm_
from django.contrib.auth.forms import UsernameField
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import User, Registration, CompCode
from .models.comp_code import CompCodeHelper


class PolicyForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['agrees_to_policy', 'opts_into_photo_review']
        widgets = {
            'agrees_to_policy': forms.RadioSelect(choices=YESNO),
            'opts_into_photo_review': forms.RadioSelect(choices=YESNO),
        }

    def __init__(self, *args, **kwargs):
        super(PolicyForm, self).__init__(*args, **kwargs)
        self.fields['agrees_to_policy'].required = True
        self.fields['opts_into_photo_review'].required = True

    def clean_agrees_to_policy(self):
        data = self.cleaned_data.get('agrees_to_policy')
        if data is not True:
            raise forms.ValidationError('You must agree to the terms to proceed.')
        return data


class VolunteerForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['applies_to_volunteer']
        widgets = {
            'is_volunteer': forms.RadioSelect(choices=YESNO),
        }

    def __init__(self, *args, **kwargs):
        super(VolunteerForm, self).__init__(*args, **kwargs)
        self.fields['is_volunteer'].required = True


class VolunteerDetailsForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = [
            'volunteer_cellphone_number',
            'volunteer_hours_max',
            'volunteer_image',
            'volunteer_skills',
            'volunteer_cantwont',
        ]
        widgets = {
            'volunteer_hours_max': forms.NumberInput(attrs={'min': 1, 'max': 8, 'value': 3})
        }

    def __init__(self, *args, **kwargs):
        super(VolunteerDetailsForm, self).__init__(*args, **kwargs)
        self.fields['volunteer_cellphone_number'].required = True
        self.fields['volunteer_hours_max'].required = True
        self.fields['volunteer_hours_max'].validators = [MinValueValidator(1), MaxValueValidator(8)]
        self.fields['volunteer_image'].required = True


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
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'input'}),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2', 'first_name', 'last_name', 'personal_pronouns', 'city', 'severe_allergies')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'input'}),
            'first_name': forms.TextInput(attrs={'class': 'input'}),
            'last_name': forms.TextInput(attrs={'class': 'input'}),
        }


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'personal_pronouns', 'city', 'severe_allergies')


# Override AuthenticationForm to apply styling class and use EmailInput widget for UsernameField
# username is actually the email address -- this translation happens in in base class.
class AuthenticationForm(AuthenticationForm_):
    username = UsernameField(widget=forms.EmailInput(attrs={'autofocus': True, 'class': 'input'}))
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'class': 'input'}),
    )
