from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Registration
from .models import User


# Register your models here.
admin.site.register(Registration)
admin.site.register(User, UserAdmin)
