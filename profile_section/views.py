from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q, Count
from .models import ContentPreference, Follow, Notification
from posts.models import Post, Like, Repost, Bookmark

User = get_user_model()


@login_required
def home_feed(request):
    tab = request.GET.get('tab', 'foryou')
    following_ids = list(
        Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
    )

    if tab == 'following':
        if following_ids:
            posts = Post.objects.filter(
                user_id__in=following_ids, is_reply=False
            ).select_related('user', 'quoted_post', 'quoted_post__user').order_by('-created_at')[:50]
        else:
            posts = Post.objects.none()
    else:
        posts = Post.objects.filter(
            is_reply=False
        ).select_related('user', 'quoted_post', 'quoted_post__user').order_by('-created_at')[:50]

    liked_ids = set(Like.objects.filter(user=request.user, post__in=posts).values_list('post_id', flat=True))
    reposted_ids = set(Repost.objects.filter(user=request.user, post__in=posts).values_list('post_id', flat=True))
    bookmarked_ids = set(Bookmark.objects.filter(user=request.user, post__in=posts).values_list('post_id', flat=True))

    suggested_users = User.objects.exclude(
        id__in=following_ids + [request.user.id]
    ).order_by('?')[:5]

    from posts.models import Hashtag
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Q

    recent_cutoff = timezone.now() - timedelta(days=7)
    trending_tags = Hashtag.objects.annotate(
        recent_count=Count('posts', filter=Q(posts__created_at__gte=recent_cutoff))
    ).filter(recent_count__gt=0).order_by('-recent_count')[:5]

    trending_ids = [t.id for t in trending_tags]

    from django.db.models import Case, When, IntegerField
    from profile_section.models import ContentPreference
    user_interests = []
    try:
        pref = request.user.content_preferences
        user_interests = pref.interests or []
    except ContentPreference.DoesNotExist:
        pass

    top_tags_qs = Hashtag.objects.exclude(id__in=trending_ids).annotate(
        post_count=Count('posts')
    ).filter(post_count__gt=0)
    if user_interests:
        interest_q = Q()
        for interest in user_interests:
            interest_q |= Q(name__icontains=interest)
        top_tags_qs = top_tags_qs.annotate(
            interest_match=Case(When(interest_q, then=1), default=0, output_field=IntegerField())
        ).order_by('-interest_match', '-post_count')
    else:
        top_tags_qs = top_tags_qs.order_by('-post_count')
    top_tags = top_tags_qs[:5]

    unread_notif_count = Notification.objects.filter(recipient=request.user, is_read=False).count()

    context = {
        'posts': posts,
        'tab': tab,
        'liked_ids': liked_ids,
        'reposted_ids': reposted_ids,
        'bookmarked_ids': bookmarked_ids,
        'suggested_users': suggested_users,
        'trending_tags': trending_tags,
        'top_tags': top_tags,
        'following_ids': following_ids,
        'unread_notif_count': unread_notif_count,
    }
    return render(request, 'feed/home.html', context)


@login_required
def profile_view(request, username=None):
    if username:
        profile_user = get_object_or_404(User, username=username)
    else:
        profile_user = request.user

    tab = request.GET.get('tab', 'posts')

    if tab == 'replies':
        posts = Post.objects.filter(user=profile_user, is_reply=True)
    elif tab == 'media':
        posts = Post.objects.filter(user=profile_user, is_reply=False).exclude(image='', video='')
    elif tab == 'likes':
        liked_post_ids = Like.objects.filter(user=profile_user).values_list('post_id', flat=True)
        posts = Post.objects.filter(id__in=liked_post_ids)
    else:
        posts = Post.objects.filter(user=profile_user, is_reply=False)

    posts = posts.select_related('user', 'quoted_post', 'quoted_post__user')

    followers_count = profile_user.followers.count()
    following_count = profile_user.following.count()
    posts_count = Post.objects.filter(user=profile_user, is_reply=False).count()
    is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists() if request.user != profile_user else False

    liked_ids = set(Like.objects.filter(user=request.user, post__in=posts).values_list('post_id', flat=True))
    reposted_ids = set(Repost.objects.filter(user=request.user, post__in=posts).values_list('post_id', flat=True))
    bookmarked_ids = set(Bookmark.objects.filter(user=request.user, post__in=posts).values_list('post_id', flat=True))

    context = {
        'profile_user': profile_user,
        'posts': posts,
        'tab': tab,
        'followers_count': followers_count,
        'following_count': following_count,
        'posts_count': posts_count,
        'is_own_profile': profile_user == request.user,
        'is_following': is_following,
        'liked_ids': liked_ids,
        'reposted_ids': reposted_ids,
        'bookmarked_ids': bookmarked_ids,
    }
    return render(request, 'profile_section/profile.html', context)


@login_required
def edit_profile(request):
    from authentication.forms import EditProfileForm
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('profile')
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'profile_section/edit_profile.html', {'form': form})


@login_required
@require_POST
def follow_user(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    if target_user == request.user:
        return JsonResponse({'status': 'error', 'message': 'Cannot follow yourself'}, status=400)

    follow_obj, created = Follow.objects.get_or_create(
        follower=request.user, following=target_user
    )
    if not created:
        follow_obj.delete()
        following = False
    else:
        following = True
        Notification.objects.create(
            recipient=target_user,
            sender=request.user,
            notification_type='follow',
            text=f'@{request.user.username} followed you'
        )

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'ok',
            'following': following,
            'followers_count': target_user.followers.count()
        })
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def followers_list(request, username):
    profile_user = get_object_or_404(User, username=username)
    follower_ids = Follow.objects.filter(following=profile_user).values_list('follower_id', flat=True)
    followers = User.objects.filter(id__in=follower_ids)
    my_following_ids = set(Follow.objects.filter(follower=request.user).values_list('following_id', flat=True))
    context = {
        'profile_user': profile_user,
        'users': followers,
        'title': 'Followers',
        'my_following_ids': my_following_ids,
    }
    return render(request, 'profile_section/follow_list.html', context)


@login_required
def following_list(request, username):
    profile_user = get_object_or_404(User, username=username)
    following_ids = Follow.objects.filter(follower=profile_user).values_list('following_id', flat=True)
    following_users = User.objects.filter(id__in=following_ids)
    my_following_ids = set(Follow.objects.filter(follower=request.user).values_list('following_id', flat=True))
    context = {
        'profile_user': profile_user,
        'users': following_users,
        'title': 'Following',
        'my_following_ids': my_following_ids,
    }
    return render(request, 'profile_section/follow_list.html', context)


@login_required
def search_view(request):
    query = request.GET.get('q', '').strip()
    tab = request.GET.get('tab', 'top')
    results = {'users': [], 'posts': []}

    if query:
        if query.startswith('#'):
            tag_name = query[1:]
            results['posts'] = Post.objects.filter(
                hashtags__name__icontains=tag_name, is_reply=False
            ).select_related('user').distinct()[:50]
        elif query.startswith('@'):
            uname = query[1:]
            results['users'] = User.objects.filter(
                Q(username__icontains=uname) | Q(display_name__icontains=uname)
            )[:20]
        else:
            if tab == 'people':
                results['users'] = User.objects.filter(
                    Q(username__icontains=query) | Q(display_name__icontains=query) | Q(bio__icontains=query)
                ).exclude(id=request.user.id)[:20]
            else:
                results['posts'] = Post.objects.filter(
                    content__icontains=query, is_reply=False
                ).select_related('user')[:50]
                results['users'] = User.objects.filter(
                    Q(username__icontains=query) | Q(display_name__icontains=query)
                ).exclude(id=request.user.id)[:5]

    my_following_ids = set(Follow.objects.filter(follower=request.user).values_list('following_id', flat=True))

    context = {
        'query': query,
        'tab': tab,
        'results': results,
        'my_following_ids': my_following_ids,
    }
    return render(request, 'profile_section/search.html', context)


@login_required
def explore_view(request):
    from posts.models import Hashtag
    from django.db.models import Count as DjCount

    trending_hashtags = Hashtag.objects.annotate(
        post_count=DjCount('posts')
    ).filter(post_count__gt=0).order_by('-post_count')[:15]

    trending_posts = Post.objects.filter(is_reply=False).annotate(
        engagement=Count('likes') + Count('reposts') + Count('replies')
    ).order_by('-engagement', '-created_at')[:20]

    trending_posts = trending_posts.select_related('user', 'quoted_post', 'quoted_post__user')

    liked_ids = set(Like.objects.filter(user=request.user, post__in=trending_posts).values_list('post_id', flat=True))
    reposted_ids = set(Repost.objects.filter(user=request.user, post__in=trending_posts).values_list('post_id', flat=True))
    bookmarked_ids = set(Bookmark.objects.filter(user=request.user, post__in=trending_posts).values_list('post_id', flat=True))

    context = {
        'trending_hashtags': trending_hashtags,
        'trending_posts': trending_posts,
        'liked_ids': liked_ids,
        'reposted_ids': reposted_ids,
        'bookmarked_ids': bookmarked_ids,
    }
    return render(request, 'profile_section/explore.html', context)


@login_required
def hashtag_view(request, tag_name):
    from posts.models import Hashtag
    posts = Post.objects.filter(
        hashtags__name__iexact=tag_name, is_reply=False
    ).select_related('user', 'quoted_post', 'quoted_post__user').distinct()

    liked_ids = set(Like.objects.filter(user=request.user, post__in=posts).values_list('post_id', flat=True))
    reposted_ids = set(Repost.objects.filter(user=request.user, post__in=posts).values_list('post_id', flat=True))
    bookmarked_ids = set(Bookmark.objects.filter(user=request.user, post__in=posts).values_list('post_id', flat=True))

    context = {
        'tag_name': tag_name,
        'posts': posts,
        'post_count': posts.count(),
        'liked_ids': liked_ids,
        'reposted_ids': reposted_ids,
        'bookmarked_ids': bookmarked_ids,
    }
    return render(request, 'profile_section/hashtag.html', context)


@login_required
def settings_view(request):
    from authentication.forms import PostSettingsForm, NotificationSettingsForm
    tab = request.GET.get('tab', 'account')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'toggle_privacy':
            request.user.is_private = not request.user.is_private
            request.user.save()
            messages.success(request, 'Privacy setting updated.')
        elif action == 'change_password':
            from django.contrib.auth import update_session_auth_hash
            old_pw = request.POST.get('old_password')
            new_pw = request.POST.get('new_password')
            confirm_pw = request.POST.get('confirm_password')
            if not request.user.check_password(old_pw):
                messages.error(request, 'Current password is incorrect.')
            elif new_pw != confirm_pw:
                messages.error(request, 'New passwords do not match.')
            elif len(new_pw) < 8:
                messages.error(request, 'Password must be at least 8 characters.')
            else:
                request.user.set_password(new_pw)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Password changed successfully.')
        elif action == 'delete_account':
            request.user.delete()
            return redirect('login')
        elif action == 'update_notifications':
            form = NotificationSettingsForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Notification settings updated.')
            tab = 'notifications'
        elif action == 'update_appearance':
            theme = request.POST.get('theme', 'dark')
            if theme in ('dark', 'dim', 'light'):
                request.user.theme = theme
                request.user.save()
                messages.success(request, 'Appearance updated.')
            tab = 'appearance'
        elif action == 'update_post_settings':
            form = PostSettingsForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Post settings updated.')
            tab = 'posts'
        elif action == 'update_account':
            new_email = request.POST.get('email', '').strip()
            if new_email and new_email != request.user.email:
                if User.objects.filter(email=new_email).exclude(pk=request.user.pk).exists():
                    messages.error(request, 'This email is already in use.')
                else:
                    request.user.email = new_email
                    request.user.save()
                    messages.success(request, 'Account updated.')
            tab = 'account'
        elif action == 'save_preferences':
            from profile_section.models import ContentPreference
            selected = request.POST.getlist('interests')
            pref, created = ContentPreference.objects.get_or_create(user=request.user)
            pref.interests = selected
            pref.preferences_completed = True
            pref.save()
            messages.success(request, 'Content preferences saved.')
            tab = 'preferences'

        if action != 'delete_account':
            return redirect(f'/profile/settings/?tab={tab}')

    post_settings_form = PostSettingsForm(instance=request.user)
    notification_form = NotificationSettingsForm(instance=request.user)

    user_posts = Post.objects.filter(user=request.user, is_reply=False).select_related('user').order_by('-created_at')[:50]

    from profile_section.models import ContentPreference
    user_interests = []
    try:
        pref = request.user.content_preferences
        user_interests = pref.interests or []
    except ContentPreference.DoesNotExist:
        pass

    context = {
        'tab': tab,
        'post_settings_form': post_settings_form,
        'notification_form': notification_form,
        'user_posts': user_posts,
        'interest_choices': ContentPreference.INTEREST_CHOICES,
        'user_interests': user_interests,
    }
    return render(request, 'profile_section/settings.html', context)


@login_required
def meta_ai_view(request):
    return render(request, 'profile_section/meta_ai.html', {'active_nav': 'meta_ai'})
