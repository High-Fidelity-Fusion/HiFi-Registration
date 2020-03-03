from django.db import models

class Registration(models.Model):
    agree_to_coc = models.BooleanField(verbose_name="Do you agree to the Code of Conduct?", null=True, blank=False)
    allergens_severe = models.TextField(verbose_name="Severe Allergies", help_text="List allergens that would be a threat to you if they were in the venue at all", max_length=828, null=True, blank=False)