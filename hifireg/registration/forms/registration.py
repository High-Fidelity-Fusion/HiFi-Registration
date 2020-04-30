from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

from registration.models import Registration, CompCode, Volunteer, CompCodeHelper

from .validators import validate_answered


YESNO = [(False, 'No'), (True, 'Yes')]


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


class RegAccessiblePriceCalcForm(forms.Form):
    prices = [1, 5, 10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100, 125, 150, 175, 200, 225, 250, 275, 300, 325, 350, 375, 400]
    price_choices = [
        (None, ''),
        (1, 'I could comfortably pay this price.'),
        (2, 'This amount would be a stretch.'),
        (3, 'I could not pay this price.')
    ]
    proceed_choices = [
        (None, ''),
        (4, 'I will pay this price.'),
        (5, 'I wish to schedule a call with the Accessibility Coordinator')
    ]

    def __init__(self, original_price, ap_eligible_amount, *args, **kwargs):
        super(RegAccessiblePriceCalcForm, self).__init__(*args, **kwargs)
        j = 0
        for i, price in enumerate(self.prices):
            if price > (original_price - ap_eligible_amount):
                if price < original_price:
                    field_name = 'price' + str(i - j)
                    self.fields[field_name] = forms.TypedChoiceField(
                        label='$'+str(price), choices=self.price_choices, coerce=int, validators=[validate_answered]
                    )
            else:
                j += 1
        self.fields['accessible_price'] = forms.IntegerField(label='', widget=forms.HiddenInput(), required=False)
        self.fields['stretch_price'] = forms.IntegerField(label='', widget=forms.HiddenInput(), required=False)
        self.fields['accessible_price_display'] = forms.CharField(
            max_length=6, label='Accessible Price:', disabled=True, required=False
        )
        self.fields['proceed'] = forms.TypedChoiceField(
            label='How should we proceed?', choices=self.proceed_choices, coerce=int, validators=[validate_answered]
        )


class RegDonateForm(forms.Form):
    donation_to_AP_fund = forms.DecimalField(
        label='I would like to contribute this dollar amount to the accessible pricing fund:', initial=0, decimal_places=2
    )
    donation_to_hifi = forms.DecimalField(
        label='I would like to provide this dollar amount of additional support to HiFi:', initial=0, decimal_places=2
    )
