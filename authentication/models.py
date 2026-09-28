from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    cover_photo = models.ImageField(upload_to='cover_photos/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(max_length=200, blank=True)
    is_private = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True, null=True)

    WHO_CAN_REPLY_CHOICES = [
        ('everyone', 'Everyone'),
        ('followers', 'People you follow'),
        ('mentioned', 'Only people you mention'),
    ]
    MEDIA_VISIBILITY_CHOICES = [
        ('everyone', 'Everyone'),
        ('followers', 'Followers only'),
        ('none', 'No one'),
    ]

    POST_VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('followers', 'Followers only'),
        ('private', 'Only me'),
    ]

    who_can_reply = models.CharField(max_length=20, choices=WHO_CAN_REPLY_CHOICES, default='everyone')
    allow_mentions = models.BooleanField(default=True)
    allow_reposts = models.BooleanField(default=True)
    allow_comments = models.BooleanField(default=True)
    allow_quote_posts = models.BooleanField(default=True)
    media_visibility = models.CharField(max_length=20, choices=MEDIA_VISIBILITY_CHOICES, default='everyone')
    default_post_visibility = models.CharField(max_length=20, choices=POST_VISIBILITY_CHOICES, default='public')
    sensitive_content_warning = models.BooleanField(default=False)
    show_likes_count = models.BooleanField(default=True)
    show_reposts_count = models.BooleanField(default=True)
    auto_save_drafts = models.BooleanField(default=True)
    allow_dm_from = models.CharField(max_length=20, choices=[('everyone', 'Everyone'), ('followers', 'People you follow'), ('none', 'No one')], default='everyone')

    email_notifications = models.BooleanField(default=True)
    push_likes = models.BooleanField(default=True)
    push_replies = models.BooleanField(default=True)
    push_follows = models.BooleanField(default=True)
    push_mentions = models.BooleanField(default=True)
    push_reposts = models.BooleanField(default=True)
    push_messages = models.BooleanField(default=True)

    theme = models.CharField(max_length=20, default='dark', choices=[('dark', 'Dark'), ('dim', 'Dim'), ('light', 'Light')])

    def __str__(self):
        return self.username

    def get_display_name(self):
        return self.display_name or self.first_name or self.username
