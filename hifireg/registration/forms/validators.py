from django.core.exceptions import ValidationError


def validate_answered(value):
    if value is None:
        raise ValidationError('This field is required.')
