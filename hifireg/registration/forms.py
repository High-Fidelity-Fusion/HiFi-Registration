from django import forms
from django.contrib.auth.forms import UserCreationForm as UserCreationForm_
from .models import User, Registration, CompCode
from .models.comp_code import CompCodeHelper
from django.core.exceptions import ValidationError

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
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')
    