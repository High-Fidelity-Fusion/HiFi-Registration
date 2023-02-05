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

CONFIRMATION_EMAIL_ENABLED = False