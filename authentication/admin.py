from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'display_name', 'is_verified', 'is_staff']
    list_filter = ['is_verified', 'is_private', 'is_staff']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('VYRO Profile', {'fields': ('display_name', 'bio', 'profile_picture', 'cover_photo', 'location', 'website', 'is_private', 'is_verified')}),
    )
