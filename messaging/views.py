from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q, Max
from .models import Conversation, Message
from profile_section.models import Notification

User = get_user_model()


@login_required
def messages_page(request):
    conversations = Conversation.objects.filter(
        participants=request.user
    ).prefetch_related('participants', 'messages').annotate(
        last_msg_time=Max('messages__created_at')
    ).order_by('-last_msg_time')

    conversation_list = []
    for conv in conversations:
        other_participants = conv.participants.exclude(id=request.user.id)
        other_user = other_participants.first()
        last_message = conv.messages.order_by('-created_at').first()
        unread_count = conv.messages.filter(is_read=False).exclude(sender=request.user).count()
        conversation_list.append({
            'conversation': conv,
            'other_user': other_user,
            'last_message': last_message,
            'unread_count': unread_count,
        })

    context = {'conversation_list': conversation_list}
    return render(request, 'messaging/messages_page.html', context)


@login_required
def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    msgs = conversation.messages.select_related('sender').all()
    other_user = conversation.participants.exclude(id=request.user.id).first()

    conversation.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    if request.method == 'POST':
        text = request.POST.get('message', '').strip()
        if text:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                text=text
            )
            conversation.save()
            if other_user:
                Notification.objects.create(
                    recipient=other_user,
                    sender=request.user,
                    notification_type='message',
                    text=f'@{request.user.username} sent you a message'
                )
            return redirect('conversation_detail', conversation_id=conversation.id)

    context = {
        'conversation': conversation,
        'messages': msgs,
        'other_user': other_user,
    }
    return render(request, 'messaging/conversation_detail.html', context)


@login_required
def new_conversation(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        if not username:
            return redirect('messages_page')
        try:
            other_user = User.objects.get(username=username)
        except User.DoesNotExist:
            from django.contrib import messages as django_messages
            django_messages.error(request, 'User not found.')
            return redirect('messages_page')

        if other_user == request.user:
            return redirect('messages_page')

        existing = Conversation.objects.filter(
            participants=request.user
        ).filter(participants=other_user)
        for conv in existing:
            if conv.participants.count() == 2:
                return redirect('conversation_detail', conversation_id=conv.id)

        conv = Conversation.objects.create()
        conv.participants.add(request.user, other_user)
        return redirect('conversation_detail', conversation_id=conv.id)

    users = User.objects.exclude(id=request.user.id).order_by('username')[:50]
    return render(request, 'messaging/new_conversation.html', {'users': users})


@login_required
def start_conversation(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    if other_user == request.user:
        return redirect('messages_page')

    existing = Conversation.objects.filter(
        participants=request.user
    ).filter(participants=other_user)
    for conv in existing:
        if conv.participants.count() == 2:
            return redirect('conversation_detail', conversation_id=conv.id)

    conv = Conversation.objects.create()
    conv.participants.add(request.user, other_user)
    return redirect('conversation_detail', conversation_id=conv.id)
