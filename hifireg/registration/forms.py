from django.forms import ModelForm
from .models import Registration

class RegistrationForm(ModelForm):
    class Meta:
        model = Registration
        fields = ['agree_to_coc','allergens_severe']