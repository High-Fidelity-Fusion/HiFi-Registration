from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_agree(value):
    if value is not True:
        raise ValidationError(_('You must agree to proceed.'))
