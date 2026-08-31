import logging
import threading

from django.conf import settings
from django.contrib import messages as django_messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Count, Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit

from .forms import SignupForm
from .models import Chat, ChatMember, FriendRequest, Interest, Message, Notification, Profile, UserPresence

logger = logging.getLogger(__name__)


def welcome(request):
    return render(request, 'welcome.html')


def terms_of_service(request):
    return render(request, 'terms.html')


def privacy_policy(request):
    return render(request, 'privacy.html')


@ratelimit(key='ip', rate='10/m', method='POST', block=False)
def login_view(request):
    if request.user.is_authenticated:
        return redirect('matches')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if request.limited:
            form.add_error(None, 'Too many login attempts. Please wait a minute and try again.')
        elif form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('matches')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


@ratelimit(key='ip', rate='10/m', method='POST', block=False)
def signup_view(request):
    if request.user.is_authenticated:
        return redirect('matches')
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if request.limited:
            form.add_error(None, 'Too many signup attempts. Please wait a minute and try again.')
        elif form.is_valid():
            user = form.save(commit=False)
            email = form.cleaned_data.get('email')
            if email:
                user.email = email
            user.save()
            profile, _ = Profile.objects.get_or_create(user=user)
            send_verification_email_async(user)
            login(request, user)
            return redirect('onboarding')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})


def send_verification_email(user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    verify_url = f"{settings.SITE_BASE_URL}/verify-email/{uid}/{token}/"
    subject = 'Verify your email — InConnect'
    html = render_to_string('emails/verify_email.html', {
        'user': user,
        'verify_url': verify_url,
    })
    try:
        send_mail(
            subject,
            f'Verify your email by visiting: {verify_url}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html,
        )
    except Exception:
        logger.warning('Failed to send verification email to %s', user.email, exc_info=True)


def send_verification_email_async(user):
    def _run():
        try:
            send_verification_email(user)
        except Exception:
            logger.warning('Failed to send verification email to %s', user.email, exc_info=True)
    t = threading.Thread(target=_run, daemon=True)
    t.start()


@ratelimit(key='ip', rate='3/h', method='POST', block=False)
def password_reset(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if request.limited:
            form.add_error('email', 'Too many reset attempts. Please try again in an hour.')
        elif form.is_valid():
            form.save(
                request=request,
                email_template_name='registration/password_reset_email.txt',
                html_email_template_name='registration/password_reset_email.html',
            )
            return redirect('password_reset_done')
    else:
        form = PasswordResetForm()
    return render(request, 'registration/password_reset_form.html', {'form': form})


def password_reset_done(request):
    return render(request, 'registration/password_reset_done.html')


def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    valid = user is not None and default_token_generator.check_token(user, token)
    if not valid:
        return render(request, 'registration/password_reset_confirm.html', {'validlink': False})

    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            return redirect('password_reset_complete')
    else:
        form = SetPasswordForm(user)
    return render(request, 'registration/password_reset_confirm.html', {'form': form, 'validlink': True})


def password_reset_complete(request):
    return render(request, 'registration/password_reset_complete.html')


@login_required
@require_POST
@ratelimit(key='user', rate='1/m', method='POST', block=True)
def resend_verification(request):
    send_verification_email_async(request.user)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'ok': True, 'message': 'Verification email sent.'})
    return redirect('verification_sent')


@login_required
def verification_sent(request):
    return render(request, 'verification_sent.html')


def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    valid = user is not None and default_token_generator.check_token(user, token)
    if valid:
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.email_verified = True
        profile.save()
    return render(request, 'email_verification.html', {'valid': valid, 'verified_email': user.email if valid else ''})


@login_required
def logout_view(request):
    logout(request)
    return redirect('welcome')


@login_required
def onboarding(request):
    interests = Interest.objects.order_by('category', 'name')
    if request.method == 'POST':
        raw = request.POST.get('interests', '')
        selected = [x for x in raw.split(',') if x]
        profile, _ = Profile.objects.get_or_create(user=request.user)
        profile.interests.set(selected)
        return redirect('matches')
    return render(request, 'onboarding_interests.html', {'interests': interests})


@login_required
def matches(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    my_interest_ids = set(profile.interests.values_list('id', flat=True))

    existing_chats = {}
    for m in request.user.chats.filter(is_group=False).prefetch_related('participants').exclude(participants=request.user):
        other = m.other_user(request.user)
        if other:
            existing_chats[other.id] = m.id

    matches_list = []
    other_profiles = Profile.objects.exclude(user=request.user).prefetch_related('interests', 'user')
    for p in other_profiles:
        p_interest_ids = set(i.id for i in p.interests.all())
        if not my_interest_ids or not p_interest_ids:
            continue
        shared_ids = my_interest_ids & p_interest_ids
        score = round(len(shared_ids) / len(my_interest_ids | p_interest_ids) * 100)
        if score > 0:
            shared = [i for i in p.interests.all() if i.id in shared_ids]
            matches_list.append({
                'profile': p,
                'score': score,
                'shared': shared,
                'existing_chat_id': existing_chats.get(p.user_id),
            })
    matches_list.sort(key=lambda m: m['score'], reverse=True)

    return render(request, 'match_discovery.html', {
        'matches': matches_list,
        'my_interests': my_interest_ids,
        'profile': profile,
    })


@login_required
def messages_list(request):
    memberships = ChatMember.objects.filter(user=request.user)
    member_map = {m.chat_id: m for m in memberships}

    other_user_qs = User.objects.exclude(id=request.user.id)

    chats = list(request.user.chats.prefetch_related(
        Prefetch('participants', queryset=other_user_qs, to_attr='_other_users'),
    ).order_by('-created_at'))

    chat_ids = [c.id for c in chats]

    last_messages = {}
    if chat_ids:
        for msg in Message.objects.filter(chat_id__in=chat_ids).order_by('chat_id', '-created_at'):
            if msg.chat_id not in last_messages:
                last_messages[msg.chat_id] = msg

    unread_map = {}
    if chat_ids:
        for chat_id, cnt in Message.objects.filter(
            chat_id__in=chat_ids, is_read=False
        ).exclude(
            sender=request.user
        ).values('chat').annotate(cnt=Count('id')).values_list('chat', 'cnt'):
            unread_map[chat_id] = cnt

    total_unread = 0
    for chat in chats:
        chat.last_message = last_messages.get(chat.id)
        chat.other = chat._other_users[0] if chat._other_users else None
        chat.unread_count = unread_map.get(chat.id, 0)
        chat.is_archived = bool(member_map.get(chat.id) and member_map[chat.id].is_archived)
        chat.is_muted = bool(member_map.get(chat.id) and member_map[chat.id].is_muted)
        total_unread += chat.unread_count

    active_chats = [c for c in chats if not c.is_archived]
    archived_chats = [c for c in chats if c.is_archived]

    return render(request, 'messages.html', {
        'chats': active_chats,
        'archived_chats': archived_chats,
        'total_unread': total_unread,
        'total_chats': len(active_chats),
        'group_chat_count': request.user.chats.filter(is_group=True).count(),
    })


@login_required
def chat_room(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, participants=request.user)
    other = chat.other_user(request.user)
    if request.method == 'POST':
        content = request.POST.get('message', '').strip()
        if content:
            Message.objects.create(chat=chat, sender=request.user, content=content)
        return redirect('chat_room', chat_id=chat.id)
    chat.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    msgs = chat.messages.select_related('sender')
    return render(request, 'chat.html', {
        'chat': chat,
        'other': other,
        'messages': msgs,
    })


@login_required
def profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, 'profile.html', {'profile': profile})


@login_required
def upload_avatar(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST' and request.FILES.get('avatar'):
        profile.avatar = request.FILES['avatar']
        profile.save()
        django_messages.success(request, "Profile picture updated.")
    return redirect('profile')


@login_required
def update_bio(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST' and request.POST.get('bio') is not None:
        profile.bio = request.POST.get('bio', '').strip()
        profile.save()
        django_messages.success(request, "Bio updated.")
    return redirect('profile')


@login_required
def update_about(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        field = request.POST.get('field', '')
        value = request.POST.get('value', '').strip()
        if field in ('location', 'hobbies', 'personality'):
            setattr(profile, field, value)
            profile.save()
            django_messages.success(request, f"{field.capitalize()} updated.")
    return redirect('profile')


@login_required
def update_zoom(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        try:
            level = int(request.POST.get('zoom', profile.zoom_level))
        except (TypeError, ValueError):
            level = profile.zoom_level
        if level in (70, 85, 100, 120, 140):
            profile.zoom_level = level
            profile.save()
            django_messages.success(request, f"Screen size set to {level}%.")
    return redirect('profile')


@login_required
def public_profile(request, user_id):
    user = get_object_or_404(request.user.__class__, id=user_id)
    profile, _ = Profile.objects.get_or_create(user=user)
    if request.user == user:
        return redirect('profile')
    chat = Chat.objects.filter(is_group=False, participants=request.user).filter(participants=user).first()
    existing_chat_id = chat.id if chat else None
    return render(request, 'public_profile.html', {
        'profile': profile,
        'viewing_user': user,
        'existing_chat_id': existing_chat_id,
    })


@login_required
def send_friend_request(request, user_id):
    other_user = get_object_or_404(request.user.__class__, id=user_id)
    if other_user == request.user:
        return redirect('matches')

    if Chat.objects.filter(is_group=False, participants=request.user).filter(participants=other_user).exists():
        return redirect('chat_room', chat_id=Chat.objects.filter(is_group=False, participants=request.user).filter(participants=other_user).first().id)

    request_obj, created = FriendRequest.objects.get_or_create(
        from_user=request.user, to_user=other_user,
        defaults={'status': FriendRequest.STATUS_PENDING},
    )
    if created:
        Notification.objects.create(
            user=other_user,
            kind=Notification.KIND_FRIEND_REQUEST,
            text=f"{request.user.username} sent you a friend request",
            actor=request.user,
        )
        django_messages.success(request, f"Friend request sent to {other_user.username}.")
    else:
        django_messages.info(request, "Friend request already pending.")
    return redirect('matches')


@login_required
def respond_request(request, request_id, action):
    friend_request = get_object_or_404(
        FriendRequest, id=request_id, to_user=request.user, status=FriendRequest.STATUS_PENDING
    )

    if action == 'accept':
        friend_request.status = FriendRequest.STATUS_ACCEPTED
        friend_request.save()
        chat = Chat.objects.filter(is_group=False, participants=request.user).filter(participants=friend_request.from_user).first()
        if not chat:
            chat = Chat.objects.create(is_group=False)
        chat.participants.add(request.user, friend_request.from_user)
        ChatMember.objects.get_or_create(chat=chat, user=request.user)
        ChatMember.objects.get_or_create(chat=chat, user=friend_request.from_user)
        Notification.objects.create(
            user=friend_request.from_user,
            kind=Notification.KIND_REQUEST_ACCEPTED,
            text=f"{request.user.username} accepted your friend request",
            actor=request.user,
        )
    elif action == 'decline':
        friend_request.status = FriendRequest.STATUS_DECLINED
        friend_request.save()

    return redirect('notifications')


@login_required
def notifications(request):
    pending_requests = list(
        FriendRequest.objects.filter(
            to_user=request.user, status=FriendRequest.STATUS_PENDING
        ).select_related('from_user')
    )

    notifs = Notification.objects.filter(user=request.user).select_related('actor')

    system_updates = [n for n in notifs if n.kind in (Notification.KIND_REQUEST_ACCEPTED, Notification.KIND_SYSTEM)]
    request_notifs = [n for n in notifs if n.kind == Notification.KIND_FRIEND_REQUEST and not n.is_read]

    Notification.objects.filter(user=request.user).update(is_read=True)

    return render(request, 'notifications.html', {
        'pending_requests': pending_requests,
        'system_updates': system_updates,
        'request_notifs': request_notifs,
        'all_notifications': notifs,
    })


@login_required
def user_search(request):
    q = request.GET.get('q', '').strip()
    results = []
    if q:
        users = User.objects.exclude(id=request.user.id).filter(
            Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q)
        ).select_related('profile').prefetch_related('profile__interests')[:20]

        my_requests = {}
        for fr in FriendRequest.objects.filter(from_user=request.user, status=FriendRequest.STATUS_PENDING):
            my_requests[fr.to_user_id] = 'pending_sent'
        for fr in FriendRequest.objects.filter(to_user=request.user, status=FriendRequest.STATUS_PENDING):
            my_requests.setdefault(fr.from_user_id, 'pending_received')

        friend_ids = set()
        for chat in request.user.chats.filter(is_group=False).prefetch_related('participants').exclude(participants=request.user):
            other = chat.other_user(request.user)
            if other:
                friend_ids.add(other.id)

        online_ids = set(
            UserPresence.objects.filter(user_id__in=[u.id for u in users], is_online=True)
            .values_list('user_id', flat=True)
        )

        for u in users:
            p = getattr(u, 'profile', None)
            status = 'accepted' if u.id in friend_ids else my_requests.get(u.id, 'none')
            results.append({
                'id': u.id,
                'username': u.username,
                'full_name': u.get_full_name() or u.username,
                'bio': p.bio if p else '',
                'avatar': p.avatar.url if p and p.avatar else '',
                'online': u.id in online_ids,
                'status': status,
            })
    return JsonResponse({'results': results})


@login_required
def start_chat(request, user_id):
    other_user = get_object_or_404(request.user.__class__, id=user_id)
    chat = Chat.objects.filter(is_group=False, participants=request.user).filter(participants=other_user).first()
    if not chat:
        chat = Chat.objects.create(is_group=False)
        chat.participants.add(request.user, other_user)
        ChatMember.objects.get_or_create(chat=chat, user=request.user)
        ChatMember.objects.get_or_create(chat=chat, user=other_user)
    return redirect('chat_room', chat_id=chat.id)


@login_required
def chat_action(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, participants=request.user)
    member = ChatMember.get_for(chat, request.user)
    action = request.POST.get('action', '')
    if action == 'archive':
        member.is_archived = True
        member.save()
    elif action == 'unarchive':
        member.is_archived = False
        member.save()
    elif action == 'mute':
        member.is_muted = True
        member.save()
    elif action == 'unmute':
        member.is_muted = False
        member.save()
    elif action == 'mark_unread':
        chat.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
        chat.messages.exclude(sender=request.user).update(is_read=False)
    elif action == 'delete':
        chat.participants.remove(request.user)
        chat.memberships.filter(user=request.user).delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        from django.http import JsonResponse
        return JsonResponse({'ok': True})
    return redirect('messages')
