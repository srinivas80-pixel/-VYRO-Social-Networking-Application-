from django.core.management.base import BaseCommand
from authentication.models import User
from profile_section.models import Notification
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Creates sample notifications for testing'

    def handle(self, *args, **options):
        self.stdout.write("Creating sample notifications...")

        # Get or create sample users
        try:
            # Get your user (the first user or create one)
            users = User.objects.all()
            if users.count() < 2:
                self.stdout.write(self.style.WARNING("Need at least 2 users. Creating sample users..."))
                user1, _ = User.objects.get_or_create(
                    username='testuser',
                    defaults={'email': 'test@example.com'}
                )
                user1.set_password('password123')
                user1.save()

            recipient = users.first()

            # Get or create sender users
            sender1, _ = User.objects.get_or_create(
                username='john_doe',
                defaults={'email': 'john@example.com'}
            )
            sender2, _ = User.objects.get_or_create(
                username='jane_smith',
                defaults={'email': 'jane@example.com'}
            )
            sender3, _ = User.objects.get_or_create(
                username='mike_wilson',
                defaults={'email': 'mike@example.com'}
            )

            # Create recent notifications (last hour)
            now = timezone.now()

            Notification.objects.create(
                recipient=recipient,
                sender=sender1,
                notification_type='like',
                text='liked your post',
                created_at=now - timedelta(minutes=15)
            )

            Notification.objects.create(
                recipient=recipient,
                sender=sender2,
                notification_type='comment',
                text='commented on your post: "Great photo!"',
                created_at=now - timedelta(minutes=30)
            )

            Notification.objects.create(
                recipient=recipient,
                sender=sender3,
                notification_type='follow',
                text='started following you',
                created_at=now - timedelta(minutes=45)
            )

            # Create 24 hours notifications
            Notification.objects.create(
                recipient=recipient,
                sender=sender1,
                notification_type='like',
                text='liked your story',
                created_at=now - timedelta(hours=5)
            )

            Notification.objects.create(
                recipient=recipient,
                sender=sender2,
                notification_type='comment',
                text='mentioned you in a comment',
                created_at=now - timedelta(hours=12)
            )

            Notification.objects.create(
                recipient=recipient,
                sender=sender3,
                notification_type='like',
                text='liked your post',
                created_at=now - timedelta(hours=20)
            )

            # Create past notifications
            Notification.objects.create(
                recipient=recipient,
                sender=sender1,
                notification_type='follow',
                text='started following you',
                created_at=now - timedelta(days=2)
            )

            Notification.objects.create(
                recipient=recipient,
                sender=sender2,
                notification_type='like',
                text='liked your post',
                created_at=now - timedelta(days=5)
            )

            Notification.objects.create(
                recipient=recipient,
                sender=sender3,
                notification_type='comment',
                text='commented: "Amazing content!"',
                created_at=now - timedelta(days=7)
            )

            self.stdout.write(self.style.SUCCESS("\nSample notifications created successfully!"))
            self.stdout.write(f"Total notifications: {Notification.objects.count()}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
