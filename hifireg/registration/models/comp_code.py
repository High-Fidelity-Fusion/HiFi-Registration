from django.db import models
import string, random

class UpperCaseCharField(models.CharField):
    def __init__(self, *args, **kwargs):
        super(UpperCaseCharField, self).__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname, None)
        if value:
            value = value.upper()
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super(UpperCaseCharField, self).pre_save(model_instance, add)

class CompCodeHelper():
    CODE_LENGTH = 5

    @classmethod
    def generate_random_code(cls):
        letters = string.ascii_letters
        return ''.join(random.choice(letters) for i in range(cls.CODE_LENGTH))

class CompCode(models.Model):
    STAFF = 'STAFF'
    ORGANIZER = 'ORGNZ'
    PARTNER = 'PRTNR'
    OTHER = 'OTHER'
    TYPES = [
        (STAFF, 'Hired Staff'),
        (ORGANIZER, 'Organizer'),
        (PARTNER, 'Partner Program'),
        (OTHER, 'Other')
    ]

    code = UpperCaseCharField(help_text='Enter a custom code or leave blank to auto generate', max_length=CompCodeHelper.CODE_LENGTH, default=CompCodeHelper.generate_random_code)
    type = models.CharField(max_length=5, choices=TYPES)
    max_uses = models.PositiveIntegerField()
    notes = models.CharField(max_length=200, null=True)