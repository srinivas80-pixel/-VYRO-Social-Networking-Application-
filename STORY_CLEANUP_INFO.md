# Story Auto-Deletion System

## How It Works

Stories in Connectify **automatically disappear after 24 hours**.

### Automatic Expiration

When a story is created:
1. `created_at` is set to current time
2. `expires_at` is automatically set to `created_at + 24 hours`

When viewing stories:
- Only stories with `expires_at > current_time` are shown
- Expired stories are automatically hidden from all views

### Database Cleanup

To keep your database clean, run the cleanup command periodically:

```bash
python manage.py cleanup_expired_stories
```

This will:
- Find all stories older than 24 hours
- Delete them from the database
- Free up storage space

### Recommended Schedule

Run the cleanup command:
- **Daily**: `python manage.py cleanup_expired_stories`
- **Or set up a cron job** (Linux/Mac):
  ```cron
  0 2 * * * cd /path/to/instagram && python manage.py cleanup_expired_stories
  ```
- **Or Windows Task Scheduler**: Schedule the command to run daily at 2 AM

### Manual Cleanup

You can run cleanup anytime:
```bash
python manage.py cleanup_expired_stories
```

Output will show:
```
Checking for expired stories...
✓ Deleted 5 expired stories
Active stories: 12
```

### Story Timer

Each story shows:
- ⏱️ Time remaining (e.g., "20h 45m remaining")
- "Expired" status if already past 24 hours
- Time posted (e.g., "3 hours ago")

### Technical Details

**Story Model:**
- `created_at`: When story was posted
- `expires_at`: Exactly 24 hours after creation
- `is_expired`: Property that checks if story is past expiration
- `time_remaining`: Shows hours and minutes left

**Automatic Filtering:**
All story queries use: `Story.objects.filter(expires_at__gt=timezone.now())`

This ensures expired stories are NEVER shown, even before cleanup runs.

### Storage

Expired story files (images/videos) are also deleted when running cleanup command.
This keeps your `media/stories/` folder clean.

## Best Practices

1. **Run cleanup daily** to keep database clean
2. **Monitor storage** in `media/stories/` folder
3. **Stories are hidden immediately** after 24 hours (no cleanup needed for visibility)
4. **Cleanup is just for database/storage** maintenance
