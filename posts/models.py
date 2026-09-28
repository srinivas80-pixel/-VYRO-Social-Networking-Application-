from django.db import models
from django.conf import settings
import re


class Hashtag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"#{self.name}"


class Post(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    content = models.TextField(max_length=500, blank=True)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    video = models.FileField(upload_to='videos/', blank=True, null=True)
    hashtags = models.ManyToManyField(Hashtag, blank=True, related_name='posts')
    is_reply = models.BooleanField(default=False)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies'
    )
    is_quote = models.BooleanField(default=False)
    quoted_post = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='quotes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"@{self.user.username}: {self.content[:50]}"

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def replies_count(self):
        return self.replies.count()

    @property
    def reposts_count(self):
        return self.reposts.count()

    @property
    def quotes_count(self):
        return self.quotes.count()

    @property
    def bookmarks_count(self):
        return self.bookmarks.count()

    def extract_hashtags(self):
        tags = set(re.findall(r'#(\w+)', self.content))
        for tag_name in tags:
            hashtag, _ = Hashtag.objects.get_or_create(name=tag_name.lower())
            self.hashtags.add(hashtag)

    def extract_mentions(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        mentions = set(re.findall(r'@(\w+)', self.content))
        mentioned_users = []
        for username in mentions:
            try:
                user = User.objects.get(username=username)
                if user != self.user:
                    mentioned_users.append(user)
            except User.DoesNotExist:
                pass
        return mentioned_users

    def get_rendered_content(self):
        content = self.content
        content = re.sub(
            r'#(\w+)',
            r'<a href="/explore/hashtag/\1/" class="hashtag">#\1</a>',
            content
        )
        content = re.sub(
            r'@(\w+)',
            r'<a href="/profile/user/\1/" class="mention">@\1</a>',
            content
        )
        return content


class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user.username} likes {self.post.id}"


class Repost(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reposts'
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reposts')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user.username} reposted {self.post.id}"


class Bookmark(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookmarks'
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} bookmarked {self.post.id}"


class Comment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} on {self.post.id}"


class Story(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='stories'
    )
    image = models.ImageField(upload_to='stories/', blank=True, null=True)
    video = models.FileField(upload_to='stories/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Stories'

    def __str__(self):
        return f"{self.user.username}'s story - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at

    @property
    def time_remaining(self):
        from django.utils import timezone
        if self.is_expired:
            return "Expired"
        delta = self.expires_at - timezone.now()
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        return f"{hours}h {minutes}m remaining"
