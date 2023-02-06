"""
Django settings for hifireg project.

Generated by 'django-admin startproject' using Django 3.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = "/media/"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'registration.apps.RegistrationConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'registration.middleware.RefreshSessions',
    'registration.middleware.CheckBetaPassword',
]

ROOT_URLCONF = 'hifireg.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'hifireg.wsgi.application'

ADMINS = [('Admin', 'seerthena@gmail.com')]


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = 'static'


# Set Argon2 as default password hash algorithm
# https://docs.djangoproject.com/en/3.0/topics/auth/passwords/#using-argon2-with-django
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]


# Custom User Model
# https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#substituting-a-custom-user-model
AUTH_USER_MODEL = 'registration.User'


# Redirect HTTP traffic to HTTPS
# https://docs.djangoproject.com/en/2.2/topics/security/#ssl-https
SECURE_SSL_REDIRECT = True


# LoginView
# https://docs.djangoproject.com/en/3.0/topics/auth/default/#django.contrib.auth.views.LoginView
LOGIN_REDIRECT_URL = '/registration/'
LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = 'login'


SESSION_COOKIE_AGE = 3600

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# Deployment host
ALLOWED_HOSTS = [os.environ.get('ALLOWED_HOSTS'), '127.0.0.1']

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql', # Only postgres is supported
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
        'USER':os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'NAME': os.environ.get('DB_NAME'),
    }
}

# LOGGING
# https://docs.djangoproject.com/en/4.1/topics/logging/#configuring-logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
    }
}

# SMTP/E-Mail
# https://docs.djangoproject.com/en/3.0/topics/email/
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = os.environ.get('EMAIL_PORT')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')

# Stripe Keys
# https://stripe.com/docs/payments/checkout/accept-a-payment
STRIPE_PUBLIC_TEST_KEY = os.environ.get('STRIPE_PUBLIC_TEST_KEY')
STRIPE_SECRET_TEST_KEY = os.environ.get('STRIPE_SECRET_TEST_KEY')

# Mailchimp Secrets
#MAILCHIMP_API_KEY = 'MAILCHIMP_API_KEY'
#MAILCHIMP_USERNAME = 'MAILCHIMP_USERNAME'
#MAILCHIMP_LIST = 'MAILCHIMP_LIST'

# Beta Password
BETA_PASSWORD = os.environ.get('BETA_PASSWORD')

SQUARE_API_KEY = os.environ.get('SQUARE_API_KEY')