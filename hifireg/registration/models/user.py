from django.contrib.auth.models import AbstractUser
from django.db import models

# Custom User Model
# https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#substituting-a-custom-user-model
class User(AbstractUser):
    personal_pronouns = models.CharField(help_text="Your preferred personal pronouns.", max_length=20, null=True, blank=True)
    city = models.CharField(help_text="Your home city.", max_length=50, null=True, blank=True)