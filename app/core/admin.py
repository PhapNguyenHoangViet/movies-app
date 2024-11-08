from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from core import models


class UserAdmin(BaseUserAdmin):
    ordering = ['user_id']
    list_display = ['email', 'name',  'dateOfBirth', 'sex', 'currentCity', 'occupation']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name', 'dateOfBirth', 'sex', 'currentCity', 'occupation')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    readonly_fields = ['last_login']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'name', 'dateOfBirth', 'sex', 'currentCity', 'occupation')}
        ),
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Movie)
admin.site.register(models.Tag)
admin.site.register(models.Rating)
admin.site.register(models.Genre)
