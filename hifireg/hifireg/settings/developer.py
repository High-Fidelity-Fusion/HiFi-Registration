"""
Django settings for hifireg project.

Developer overrides for deployment secrets.

Override/mutate anything from settings/common.py or settings/secret.py here.

DO NOT COMMIT
"""

from .public import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

SECURE_SSL_REDIRECT = False

# TODO: Update this with the name of your personal developer database
DATABASES['default']['NAME'] = ''

BETA_PASSWORD = ''

CONFIRMATION_EMAIL_ENABLED = False