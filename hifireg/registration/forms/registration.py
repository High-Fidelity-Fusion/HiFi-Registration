from django.conf import settings
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

from registration.models import CompCode, Order, Registration, Volunteer, CompCodeHelper


YESNO = [(False, 'No'), (True, 'Yes')]


class BetaPasswordForm(forms.Form):
    beta_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('beta_password')
        if password != settings.BETA_PASSWORD:
            raise forms.ValidationError('Beta password is not correct')


class RegPolicyForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['agrees_to_policy', 'opts_into_photo_review']
        widgets = {
            'agrees_to_policy': forms.Select(choices=YESNO),
            'opts_into_photo_review': forms.Select(choices=YESNO),
        }

    def __init__(self, *args, **kwargs):
        super(RegPolicyForm, self).__init__(*args, **kwargs)
        self.fields['agrees_to_policy'].required = True
        self.fields['agrees_to_policy'].default = False
        self.fields['opts_into_photo_review'].required = True
        self.fields['opts_into_photo_review'].default = False

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
            'wants_to_volunteer': forms.Select(choices=YESNO),
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
            'mailing_list': forms.Select(choices=YESNO),
            'housing_transport_acknowledgement': forms.Select(choices=YESNO),
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


class RegDonateForm(forms.Form):
    donation = forms.IntegerField(
        label='I would like to contribute this dollar amount:', initial=0
    )
