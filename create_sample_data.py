"""
Script to create sample data for testing
Run this with: python manage.py shell < create_sample_data.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instagram.settings')
django.setup()

from authentication.models import User
from posts.models import Post, Story
from django.utils import timezone
from datetime import timedelta

print("Creating sample data...")

# Create sample users
usernames = ['john_doe', 'jane_smith', 'travel_enthusiast', 'foodie_life', 'music_lover']
sample_users = []

for username in usernames:
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': f'{username}@example.com',
            'first_name': username.split('_')[0].title(),
            'last_name': username.split('_')[1].title() if '_' in username else '',
        }
    )
    if created:
        user.set_password('password123')
        user.save()
        print(f"Created user: {username}")
    sample_users.append(user)

# Create sample posts
post_captions = [
    "Beautiful sunset today! 🌅",
    "Amazing food at the new restaurant downtown 🍕",
    "Traveling through Europe has been incredible! ✈️",
    "New music vibes 🎵",
    "Nature walk this morning 🌿",
    "Coffee and good books ☕📚",
    "Workout complete! 💪",
    "Art gallery visit today 🎨",
]

for i, user in enumerate(sample_users):
    # Create 2-3 posts per user
    for j in range(2):
        if i * 2 + j < len(post_captions):
            Post.objects.create(
                user=user,
                caption=post_captions[i * 2 + j],
                post_type='post',
                likes_count=10 + (i * 5)
            )
    print(f"Created posts for {user.username}")

# Create sample stories
for user in sample_users[:3]:
    Story.objects.create(
        user=user,
        expires_at=timezone.now() + timedelta(hours=24)
    )
print(f"Created stories for {sample_users[:3]}")

print("\nSample data created successfully!")
print(f"Total users: {User.objects.count()}")
print(f"Total posts: {Post.objects.count()}")
print(f"Total stories: {Story.objects.count()}")
