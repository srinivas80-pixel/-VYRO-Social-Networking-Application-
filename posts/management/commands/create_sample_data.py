from django.core.management.base import BaseCommand
from authentication.models import User
from posts.models import Post, Story
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Creates sample data for testing'

    def handle(self, *args, **options):
        self.stdout.write("Creating sample data...")

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
                self.stdout.write(self.style.SUCCESS(f"Created user: {username}"))
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
                    Post.objects.get_or_create(
                        user=user,
                        caption=post_captions[i * 2 + j],
                        defaults={
                            'post_type': 'post',
                            'likes_count': 10 + (i * 5)
                        }
                    )
            self.stdout.write(f"Created posts for {user.username}")

        # Create sample stories
        for user in sample_users[:3]:
            Story.objects.get_or_create(
                user=user,
                defaults={
                    'expires_at': timezone.now() + timedelta(hours=24)
                }
            )
        self.stdout.write(f"Created stories for users")

        self.stdout.write(self.style.SUCCESS("\nSample data created successfully!"))
        self.stdout.write(f"Total users: {User.objects.count()}")
        self.stdout.write(f"Total posts: {Post.objects.count()}")
        self.stdout.write(f"Total stories: {Story.objects.count()}")
