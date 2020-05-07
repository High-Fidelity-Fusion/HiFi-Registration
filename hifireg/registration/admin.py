from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UserAdmin_, Group
from django.utils.translation import gettext_lazy as _

from .models import CompCode, Product, ProductCategory, ProductSlot, Registration
from .models import User


class UserAdmin(UserAdmin_):
    """Define admin model for custom User model with no email field."""

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'personal_pronouns', 'city',)}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    readonly_fields = ('email', 'last_login', 'date_joined')


# Register custom User and UserAdmin
# admin.site.register(User, UserAdmin)

# Register your models here.
admin.site.register(CompCode)
admin.site.register(Product)
admin.site.register(ProductCategory)
admin.site.register(ProductSlot)

#
admin.site.unregister(Group)

