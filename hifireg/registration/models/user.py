from django.contrib.auth.models import AbstractUser, UserManager as UserManager_
from django.db import models
from django.utils.translation import gettext_lazy as _
from .utils import get_obfuscated_upload_to


# This website was initially used as a reference for how to implement a user model without an explicit username:
# https://www.fomfus.com/articles/how-to-use-email-as-username-for-django-authentication-removing-the-username
# Much of the example code appears to have been copied from the Django source and modified accordingly.

# We must create a custom UserManager for our custom User (below)
# We override UserManager instead of using BaseUserManager because we don't need to reimplement
# everything in Django's UserManager. The functions in our custom UserManager are copied straight 
# from Django source for UserManager, but have been updated for use with a User that does not 
# define a username.
class UserManager(UserManager_):
    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


# Custom User model
# https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#substituting-a-custom-user-model
class User(AbstractUser):
    # remove explicit username and use email as username instead
    username = None
    email = models.EmailField(_('email address'), unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] # no required fields

    # other profile items
    personal_pronouns = models.CharField(help_text="example: they/them/theirs", max_length=20, null=True, blank=True)
    city = models.CharField(help_text="Your home city.", max_length=50, null=True, blank=True)
    severe_allergies = models.TextField(verbose_name="Severe Allergies", help_text="List allergens that would be a threat to you if they were present in the venue.", max_length=1000, null=True, blank=True)
    covid_vaccine_picture = models.ImageField(upload_to=get_obfuscated_upload_to("covid"), verbose_name="COVID Vaccine or Exemption", help_text="Upload a picture of your COVID-19 vaccination card or a doctor note permissing an exemption. This may be required for some events.", null=True, blank=True)

    # set model manager
    objects = UserManager()
