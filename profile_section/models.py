from django.db import models
from django.conf import settings


class ContentPreference(models.Model):
    INTEREST_CHOICES = [
        ('technology', 'Technology'),
        ('sports', 'Sports'),
        ('music', 'Music'),
        ('gaming', 'Gaming'),
        ('news', 'News'),
        ('entertainment', 'Entertainment'),
        ('science', 'Science'),
        ('politics', 'Politics'),
        ('fashion', 'Fashion'),
        ('art', 'Art'),
        ('food', 'Food'),
        ('travel', 'Travel'),
        ('fitness', 'Fitness'),
        ('photography', 'Photography'),
        ('business', 'Business'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='content_preferences'
    )
    interests = models.JSONField(default=list, blank=True)
    preferences_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s preferences"

    class Meta:
        verbose_name = 'Content Preference'
        verbose_name_plural = 'Content Preferences'


class Follow(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following'
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='followers'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('follow', 'Follow'),
        ('mention', 'Mention'),
        ('repost', 'Repost'),
        ('quote', 'Quote'),
        ('message', 'Message'),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_notifications'
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    post = models.ForeignKey(
        'posts.Post',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    text = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sender.username} → {self.recipient.username}: {self.notification_type}"
