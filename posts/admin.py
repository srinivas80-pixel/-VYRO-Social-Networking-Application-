from django.contrib import admin
from .models import Post, Like, Comment, Story, Repost, Bookmark, Hashtag


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['user', 'content', 'is_reply', 'is_quote', 'created_at']
    list_filter = ['is_reply', 'is_quote', 'created_at']
    search_fields = ['user__username', 'content']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'text', 'created_at']


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'expires_at']


@admin.register(Repost)
class RepostAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']


@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
