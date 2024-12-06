from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core import models


class UserAdmin(BaseUserAdmin):
    ordering = ['user_id']
    list_display = [
        'user_id', 'email', 'name', 'dateOfBirth', 'sex', 'age', 'occupation']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'dateOfBirth', 'age', 'sex', 'currentCity', 'occupation')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important Dates', {'fields': ('last_login',)}),
    )
    readonly_fields = ['last_login']
    # Fieldset for adding a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'name', 'dateOfBirth', 'sex', 'age', 'occupation'),
        }),
    )

admin.site.register(models.User, UserAdmin)
admin.site.register(models.Movie)
admin.site.register(models.Tag)
admin.site.register(models.Rating)
admin.site.register(models.Genre)
admin.site.register(models.Comment)
admin.site.register(models.Chat)
