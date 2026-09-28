from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Notification


@login_required
def notifications_page(request):
    all_notifs = Notification.objects.filter(recipient=request.user)
    unread_count = all_notifs.filter(is_read=False).count()

    notifications = all_notifs.select_related('sender', 'post').order_by('-created_at')[:50]

    if request.method == 'POST' and request.POST.get('action') == 'mark_all_read':
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'ok'})
        return redirect('notifications')

    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)

    context = {
        'notifications': notifications,
        'unread_count': unread_count,
    }
    return render(request, 'profile_section/notifications.html', context)


@login_required
def notification_redirect(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, recipient=request.user)
    notif.is_read = True
    notif.save()

    if notif.notification_type == 'message':
        from messaging.models import Conversation
        conversations = Conversation.objects.filter(
            participants=request.user
        ).filter(participants=notif.sender)
        for conv in conversations:
            if conv.participants.count() == 2:
                return redirect('conversation_detail', conversation_id=conv.id)
        return redirect('messages_page')

    if notif.notification_type == 'follow':
        return redirect('profile_user', username=notif.sender.username)

    if notif.post:
        return redirect('post_detail', post_id=notif.post.id)

    return redirect('notifications')
