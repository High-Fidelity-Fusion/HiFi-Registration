from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm as UserCreationForm_

from .models import User, Registration

class RegistrationForm(ModelForm):
    class Meta:
        model = Registration
        fields = ['agree_to_coc','allergens_severe']

# Custom UserCreationForm for our custom User
class UserCreationForm(UserCreationForm_):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')
    