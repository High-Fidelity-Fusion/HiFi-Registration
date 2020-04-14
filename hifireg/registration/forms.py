from django import forms
from django.contrib.auth.forms import AuthenticationForm as AuthenticationForm_
from django.contrib.auth.forms import UserCreationForm as UserCreationForm_
from django.contrib.auth.forms import UsernameField
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

from .models import User, Registration, CompCode, Volunteer
from .models.comp_code import CompCodeHelper


YESNO = [(True, 'Yes'), (False, 'No')]


class RegPolicyForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['agrees_to_policy', 'opts_into_photo_review']
        widgets = {
            'agrees_to_policy': forms.RadioSelect(choices=YESNO),
            'opts_into_photo_review': forms.RadioSelect(choices=YESNO),
        }

    def __init__(self, *args, **kwargs):
        super(RegPolicyForm, self).__init__(*args, **kwargs)
        self.fields['agrees_to_policy'].required = True
        self.fields['opts_into_photo_review'].required = True

    def clean_agrees_to_policy(self):
        data = self.cleaned_data.get('agrees_to_policy')
        if data is not True:
            raise forms.ValidationError('You must agree to the terms to proceed.')
        return data


class RegVolunteerForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['wants_to_volunteer']
        widgets = {
            'wants_to_volunteer': forms.RadioSelect(choices=YESNO),
        }

    def __init__(self, *args, **kwargs):
        super(RegVolunteerForm, self).__init__(*args, **kwargs)
        self.fields['wants_to_volunteer'].required = True


class RegVolunteerDetailsForm(forms.ModelForm):
    class Meta:
        model = Volunteer
        fields = [
            'cellphone_number',
            'hours_max',
            'image',
            'skills',
            'cantwont',
        ]
        widgets = {
            'hours_max': forms.NumberInput(attrs={'min': 1, 'max': 8, 'value': 3})
        }

    def __init__(self, *args, **kwargs):
        super(RegVolunteerDetailsForm, self).__init__(*args, **kwargs)
        self.fields['cellphone_number'].required = True
        self.fields['hours_max'].required = True
        self.fields['hours_max'].validators = [MinValueValidator(1), MaxValueValidator(8)]
        self.fields['image'].required = True


class RegMiscForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = [
            'mailing_list',
            'housing_transport_acknowledgement',
            'accommodations',
            'referral_code',
            'registration_feedback',
        ]
        widgets = {
            'mailing_list': forms.RadioSelect(choices=YESNO),
            'housing_transport_acknowledgement': forms.RadioSelect(choices=YESNO),
        }

    def __init__(self, *args, **kwargs):
        super(RegMiscForm, self).__init__(*args, **kwargs)
        self.fields['mailing_list'].required = True
        self.fields['housing_transport_acknowledgement'].required = True

    def clean_housing_transport_acknowledgement(self):
        data = self.cleaned_data.get('housing_transport_acknowledgement')
        if data is not True:
            raise forms.ValidationError('You must attend to your own housing and transportation needs.')
        return data


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
