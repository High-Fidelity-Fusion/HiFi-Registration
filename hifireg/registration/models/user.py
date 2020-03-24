from django.contrib.auth.models import AbstractUser

# Custom User Model
# https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#substituting-a-custom-user-model
class User(AbstractUser):
    pass