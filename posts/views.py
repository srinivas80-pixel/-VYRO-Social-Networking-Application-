import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta
from .models import Post, Like, Repost, Bookmark, Comment, Story, Hashtag
from .forms import PostForm
from profile_section.models import Notification


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            post.extract_hashtags()
            mentioned_users = post.extract_mentions()
            for mentioned_user in mentioned_users:
                Notification.objects.create(
                    recipient=mentioned_user,
                    sender=request.user,
                    notification_type='mention',
                    post=post,
                    text=f'@{request.user.username} mentioned you in a post'
                )
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'ok', 'post_id': post.id})
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    replies = post.replies.select_related('user').order_by('-created_at')
    user_liked = post.likes.filter(user=request.user).exists()
    user_reposted = post.reposts.filter(user=request.user).exists()
    user_bookmarked = post.bookmarks.filter(user=request.user).exists()

    context = {
        'post': post,
        'replies': replies,
        'user_liked': user_liked,
        'user_reposted': user_reposted,
        'user_bookmarked': user_bookmarked,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
@require_POST
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
        if post.user != request.user:
            Notification.objects.create(
                recipient=post.user,
                sender=request.user,
                notification_type='like',
                post=post,
                text=f'@{request.user.username} liked your post'
            )
    return JsonResponse({
        'status': 'ok',
        'liked': liked,
        'count': post.likes.count()
    })


@login_required
@require_POST
def repost(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    repost_obj, created = Repost.objects.get_or_create(user=request.user, post=post)
    if not created:
        repost_obj.delete()
        reposted = False
    else:
        reposted = True
        if post.user != request.user:
            Notification.objects.create(
                recipient=post.user,
                sender=request.user,
                notification_type='repost',
                post=post,
                text=f'@{request.user.username} reposted your post'
            )
    return JsonResponse({
        'status': 'ok',
        'reposted': reposted,
        'count': post.reposts.count()
    })


@login_required
@require_POST
def bookmark_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    bm, created = Bookmark.objects.get_or_create(user=request.user, post=post)
    if not created:
        bm.delete()
        bookmarked = False
    else:
        bookmarked = True
    return JsonResponse({
        'status': 'ok',
        'bookmarked': bookmarked,
        'count': post.bookmarks.count()
    })


@login_required
@require_POST
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    text = request.POST.get('text', '').strip()
    if not text:
        return JsonResponse({'status': 'error', 'message': 'Comment cannot be empty'}, status=400)
    comment = Comment.objects.create(user=request.user, post=post, text=text)
    if post.user != request.user:
        Notification.objects.create(
            recipient=post.user,
            sender=request.user,
            notification_type='comment',
            post=post,
            text=f'@{request.user.username} replied to your post'
        )
    pic_url = request.user.profile_picture.url if request.user.profile_picture else ''
    return JsonResponse({
        'status': 'ok',
        'comment': {
            'id': comment.id,
            'user': comment.user.username,
            'display_name': comment.user.get_display_name(),
            'profile_picture': pic_url,
            'text': comment.text,
            'created_at': comment.created_at.isoformat(),
        },
        'count': post.comments.count()
    })


@login_required
@require_POST
def reply_to_post(request, post_id):
    parent_post = get_object_or_404(Post, id=post_id)
    content = request.POST.get('content', '').strip()
    if not content:
        return JsonResponse({'status': 'error', 'message': 'Reply cannot be empty'}, status=400)

    reply = Post.objects.create(
        user=request.user,
        content=content,
        is_reply=True,
        parent=parent_post
    )
    reply.extract_hashtags()
    mentioned_users = reply.extract_mentions()
    for u in mentioned_users:
        Notification.objects.create(
            recipient=u, sender=request.user,
            notification_type='mention', post=reply,
            text=f'@{request.user.username} mentioned you in a reply'
        )
    if parent_post.user != request.user:
        Notification.objects.create(
            recipient=parent_post.user,
            sender=request.user,
            notification_type='comment',
            post=parent_post,
            text=f'@{request.user.username} replied to your post'
        )
    pic_url = request.user.profile_picture.url if request.user.profile_picture else ''
    return JsonResponse({
        'status': 'ok',
        'reply': {
            'id': reply.id,
            'user': reply.user.username,
            'display_name': reply.user.get_display_name(),
            'profile_picture': pic_url,
            'content': reply.content,
            'created_at': reply.created_at.isoformat(),
        },
        'count': parent_post.replies.count()
    })


@login_required
def quote_post(request, post_id):
    quoted = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            post = Post.objects.create(
                user=request.user,
                content=content,
                is_quote=True,
                quoted_post=quoted
            )
            post.extract_hashtags()
            if quoted.user != request.user:
                Notification.objects.create(
                    recipient=quoted.user,
                    sender=request.user,
                    notification_type='quote',
                    post=post,
                    text=f'@{request.user.username} quoted your post'
                )
            return redirect('home')
    return render(request, 'posts/quote_post.html', {'quoted_post': quoted})


@login_required
@require_POST
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)
    post.delete()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok'})
    messages.success(request, 'Post deleted.')
    return redirect('home')


@login_required
def bookmarks_page(request):
    bookmarked = Bookmark.objects.filter(user=request.user).select_related('post', 'post__user')
    posts = [b.post for b in bookmarked]
    return render(request, 'posts/bookmarks.html', {'posts': posts})


@login_required
def share_users(request):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    from profile_section.models import Follow
    following_ids = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
    users = User.objects.filter(id__in=following_ids).order_by('username')[:30]
    if not users.exists():
        users = User.objects.exclude(id=request.user.id).order_by('username')[:30]
    user_list = []
    for u in users:
        user_list.append({
            'username': u.username,
            'display_name': u.get_display_name(),
            'profile_picture': u.profile_picture.url if u.profile_picture else '',
        })
    return JsonResponse({'users': user_list})


@login_required
@require_POST
def share_to_dm(request):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    from messaging.models import Conversation, Message
    post_id = request.POST.get('post_id')
    username = request.POST.get('username')
    post = get_object_or_404(Post, id=post_id)
    other_user = get_object_or_404(User, username=username)

    existing = Conversation.objects.filter(
        participants=request.user
    ).filter(participants=other_user)
    conv = None
    for c in existing:
        if c.participants.count() == 2:
            conv = c
            break
    if not conv:
        conv = Conversation.objects.create()
        conv.participants.add(request.user, other_user)

    post_url = request.build_absolute_uri(f'/posts/{post.id}/')
    text = f"Shared a post: {post_url}"
    if post.content:
        text = f'"{post.content[:100]}"\n{post_url}'
    Message.objects.create(conversation=conv, sender=request.user, text=text)
    conv.save()

    Notification.objects.create(
        recipient=other_user,
        sender=request.user,
        notification_type='message',
        text=f'@{request.user.username} shared a post with you'
    )
    return JsonResponse({'status': 'ok'})
