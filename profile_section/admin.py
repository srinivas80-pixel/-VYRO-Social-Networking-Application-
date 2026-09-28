from django.contrib import admin
from .models import ContentPreference, Follow, Notification

@admin.register(ContentPreference)
class ContentPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'preferences_completed', 'created_at', 'updated_at']
    list_filter = ['preferences_completed', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['follower', 'following', 'created_at']
    list_filter = ['created_at']
    search_fields = ['follower__username', 'following__username']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'sender', 'notification_type', 'text', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['recipient__username', 'sender__username', 'text']
    readonly_fields = ['created_at']
