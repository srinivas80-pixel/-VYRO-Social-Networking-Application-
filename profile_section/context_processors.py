def notifications_count(request):
    if request.user.is_authenticated:
        from .models import Notification
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return {'unread_notif_count': count}
    return {'unread_notif_count': 0}


def sidebar_data(request):
    if request.user.is_authenticated:
        from django.contrib.auth import get_user_model
        from django.db.models import Count, Q, Case, When, IntegerField
        from django.utils import timezone
        from datetime import timedelta, date
        from posts.models import Hashtag
        from .models import Follow, ContentPreference

        User = get_user_model()

        following_ids = list(
            Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
        )

        recent_cutoff = timezone.now() - timedelta(days=7)
        trending_tags = Hashtag.objects.annotate(
            recent_count=Count('posts', filter=Q(posts__created_at__gte=recent_cutoff))
        ).filter(recent_count__gt=0).order_by('-recent_count')[:5]

        top_tags_ids = [t.id for t in trending_tags]

        user_interests = []
        try:
            pref = request.user.content_preferences
            user_interests = pref.interests or []
        except ContentPreference.DoesNotExist:
            pass

        top_tags_qs = Hashtag.objects.exclude(id__in=top_tags_ids).annotate(
            post_count=Count('posts')
        ).filter(post_count__gt=0)

        if user_interests:
            interest_q = Q()
            for interest in user_interests:
                interest_q |= Q(name__icontains=interest)
            top_tags_qs = top_tags_qs.annotate(
                interest_match=Case(
                    When(interest_q, then=1),
                    default=0,
                    output_field=IntegerField()
                )
            ).order_by('-interest_match', '-post_count')
        else:
            top_tags_qs = top_tags_qs.order_by('-post_count')

        top_tags = top_tags_qs[:5]

        suggested_users = User.objects.exclude(
            id__in=following_ids + [request.user.id]
        ).order_by('?')[:3]

        is_birthday = False
        if request.user.date_of_birth:
            today = date.today()
            dob = request.user.date_of_birth
            if today.month == dob.month and today.day == dob.day:
                is_birthday = True

        return {
            'global_trending_tags': trending_tags,
            'global_top_tags': top_tags,
            'global_suggested_users': suggested_users,
            'global_following_ids': following_ids,
            'is_birthday': is_birthday,
        }
    return {}
