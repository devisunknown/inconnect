from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from cloudinary.models import CloudinaryField

class Interest(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, blank=True, default='')
    category = models.CharField(max_length=50, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    interests = models.ManyToManyField(Interest, blank=True, related_name='profiles')
    avatar = CloudinaryField("image", blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, default='')
    hobbies = models.CharField(max_length=255, blank=True, default='')
    personality = models.CharField(max_length=50, blank=True, default='')
    zoom_level = models.PositiveIntegerField(default=100)
    email_verified = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username

    def match_score(self, other):
        if not self.pk or not other.pk:
            return 0
        mine = set(self.interests.values_list('id', flat=True))
        theirs = set(other.interests.values_list('id', flat=True))
        if not mine or not theirs:
            return 0
        return round(len(mine & theirs) / max(len(mine | theirs), 1) * 100)


class Chat(models.Model):
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chats')
    interest = models.ForeignKey(Interest, on_delete=models.SET_NULL, null=True, blank=True, related_name='chats')
    created_at = models.DateTimeField(auto_now_add=True)
    is_group = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['-created_at'], name='chat_created_idx'),
        ]

    def __str__(self):
        return ', '.join(u.username for u in self.participants.all())

    def other_user(self, user):
        others = self.participants.exclude(id=user.id)
        return others.first()


class ChatMember(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_memberships')
    is_archived = models.BooleanField(default=False)
    is_muted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('chat', 'user')
        indexes = [
            models.Index(fields=['user', 'is_archived'], name='chatmember_user_arch_idx'),
        ]

    def __str__(self):
        return f'{self.user.username} in {self.chat_id}'

    @classmethod
    def get_for(cls, chat, user):
        obj, _ = cls.objects.get_or_create(chat=chat, user=user)
        return obj


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['chat', 'created_at'], name='message_chat_created_idx'),
            models.Index(fields=['chat', 'is_read'], name='message_chat_read_idx'),
        ]

    def __str__(self):
        return f'{self.sender.username}: {self.content[:30]}'


class FriendRequest(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_DECLINED = 'declined'

    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_requests')
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_requests')
    status = models.CharField(max_length=10, default=STATUS_PENDING, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')
        indexes = [
            models.Index(fields=['to_user', 'status'], name='friendreq_to_status_idx'),
        ]

    def __str__(self):
        return f'{self.from_user.username} -> {self.to_user.username} ({self.status})'


class UserPresence(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='presence')
    is_online = models.BooleanField(default=False, db_index=True)
    last_seen = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username}: {"online" if self.is_online else "offline"}'


class Notification(models.Model):
    KIND_FRIEND_REQUEST = 'friend_request'
    KIND_REQUEST_ACCEPTED = 'request_accepted'
    KIND_SYSTEM = 'system'

    KIND_CHOICES = [
        (KIND_FRIEND_REQUEST, 'Friend Request'),
        (KIND_REQUEST_ACCEPTED, 'Request Accepted'),
        (KIND_SYSTEM, 'System'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    kind = models.CharField(max_length=20, choices=KIND_CHOICES)
    text = models.CharField(max_length=255)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read'], name='notif_user_read_idx'),
        ]

    def __str__(self):
        return f'{self.user.username}: {self.text}'