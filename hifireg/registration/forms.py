from django.forms import ModelForm
from django import forms
from .models import Registration
from .validators import validate_agree

class policy_form(ModelForm):
    class Meta:
        model = Registration
        fields = ['agree_to_coc', 'allergens_severe']

    def formtype(self):
        return 'policy_form'

class accessibility_form(ModelForm):
    class Meta:
        model = Registration
        fields = ['allergens_severe']

    def formtype(self):
        return 'accessibility_form'

# class tmpedit(forms.Form):
#     index = forms.IntegerField(label='Entry:', initial=1, min_value=1)
#     def __init__(self, *args, **kwargs):
#         maxindex = kwargs.pop('maxindex', None)
#         super(tmpedit, self).__init__(*args, **kwargs)
#         if maxindex:
#             self.fields['index'] = forms.IntegerField(label='Entry:', initial=0, min_value=0, max_value=maxindex)

