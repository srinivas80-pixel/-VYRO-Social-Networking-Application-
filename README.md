# Instagram Clone

A full-featured Instagram clone built with Django, featuring posts, reels, stories, messaging, and user profiles.

## Features

### Authentication
- ✅ User Registration with username, email, password
- ✅ Login/Logout functionality
- ✅ Custom User model with profile pictures and bio

### Content Preferences
- ✅ Personalized interest selection (15 categories)
- ✅ Travel, Nature, Food, Movies, Music, Sports, Fashion, Art, Technology, Fitness, Photography, Gaming, Books, Pets, Business
- ✅ Beautiful visual grid interface

### Main Feed
- ✅ Instagram-style navigation bar
- ✅ Stories section with horizontal scroll
- ✅ Post feed with images and captions
- ✅ Like, comment, share, and bookmark actions
- ✅ Sidebar with user profile and suggestions
- ✅ Real-time notification badges

### Posts & Reels
- ✅ Create posts with images
- ✅ Reels support (video posts)
- ✅ Captions and hashtags
- ✅ Like counter
- ✅ Comment system
- ✅ Timestamp display

### Stories
- ✅ 24-hour expiring stories
- ✅ Image and video support
- ✅ Story viewer interface

### Profile
- ✅ User profile pages
- ✅ Posts/Reels/Tagged tabs
- ✅ Follower/Following counts
- ✅ Bio and profile picture
- ✅ Edit profile functionality
- ✅ Profile grid view for posts

### Messaging
- ✅ Direct message conversations
- ✅ Unread message notifications
- ✅ Message threads

### Social Features
- ✅ Follow/Unfollow system
- ✅ User suggestions
- ✅ Search functionality

## Pages

1. **Registration**: `/auth/register/`
2. **Login**: `/auth/login/`
3. **Content Preferences**: `/profile/preferences/`
4. **Main Feed**: `/profile/feed/`
5. **User Profile**: `/profile/` or `/profile/<username>/`
6. **Home**: `/`

## Installation & Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run migrations:
```bash
python manage.py migrate
```

3. Create sample data (optional):
```bash
python manage.py create_sample_data
```

4. Create a superuser:
```bash
python manage.py createsuperuser
```

5. Run the development server:
```bash
python manage.py runserver
```

6. Visit: http://127.0.0.1:8000/

## Sample Users

If you ran the sample data command, you can login with:
- Username: `john_doe`, `jane_smith`, `travel_enthusiast`, etc.
- Password: `password123`

## Models

### User (authentication)
- Custom user model with profile picture, bio, and date of birth

### Post (posts)
- Posts and Reels with images/videos, captions, likes

### Story (posts)
- 24-hour expiring content

### Like (posts)
- User likes on posts

### Comment (posts)
- Comments on posts

### Message (messaging)
- Direct messages between users

### Conversation (messaging)
- Message threads

### ContentPreference (profile_section)
- User interest preferences

### Follow (profile_section)
- Follower/Following relationships

## Technologies Used

- Django 6.0.5
- Python 3.x
- SQLite (default database)
- HTML/CSS (Instagram-style UI)
- JavaScript (interactive features)

## Admin Panel

Access the admin panel at: http://127.0.0.1:8000/admin/

## Future Enhancements

- Video upload for reels
- Live stories viewer
- Direct messaging interface
- Notifications system
- Explore page
- Hashtag functionality
- Post sharing
- Save collections
- Multi-image posts (carousel)
- Video calls
- Filters and effects

## License

This is a learning project for educational purposes.
