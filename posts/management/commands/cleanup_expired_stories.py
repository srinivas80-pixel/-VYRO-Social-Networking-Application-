from django.core.management.base import BaseCommand
from posts.models import Story
from django.utils import timezone


class Command(BaseCommand):
    help = 'Deletes expired stories (older than 24 hours)'

    def handle(self, *args, **options):
        self.stdout.write("Checking for expired stories...")

        # Get all expired stories
        now = timezone.now()
        expired_stories = Story.objects.filter(expires_at__lte=now)
        count = expired_stories.count()

        if count > 0:
            # Delete expired stories
            expired_stories.delete()
            self.stdout.write(
                self.style.SUCCESS(f"✓ Deleted {count} expired stor{'y' if count == 1 else 'ies'}")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("✓ No expired stories to delete")
            )

        # Show active stories count
        active_count = Story.objects.filter(expires_at__gt=now).count()
        self.stdout.write(f"Active stories: {active_count}")
