from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Chat, ChatMember, FriendRequest, Interest, Message, Notification, Profile, UserPresence


class ProfileInline(admin.StackedInline):
    model = Profile


class ProfileAdmin(admin.ModelAdmin):
    filter_horizontal = ('interests',)


class InterestAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'category')
    search_fields = ('name', 'category')


class ChatAdmin(admin.ModelAdmin):
    filter_horizontal = ('participants',)
    list_display = ('id', 'interest', 'is_group', 'created_at')


class MessageAdmin(admin.ModelAdmin):
    list_display = ('chat', 'sender', 'content', 'created_at', 'is_read')
    list_filter = ('is_read',)


class ChatMemberAdmin(admin.ModelAdmin):
    list_display = ('chat', 'user', 'is_archived', 'is_muted', 'created_at')
    list_filter = ('is_archived', 'is_muted')


class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('from_user__username', 'to_user__username')


class UserPresenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_online', 'last_seen')
    list_filter = ('is_online',)


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'kind', 'text', 'is_read', 'created_at')
    list_filter = ('kind', 'is_read')
    search_fields = ('text', 'user__username')


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Interest, InterestAdmin)
admin.site.register(Chat, ChatAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(ChatMember, ChatMemberAdmin)
admin.site.register(FriendRequest, FriendRequestAdmin)
admin.site.register(UserPresence, UserPresenceAdmin)
admin.site.register(Notification, NotificationAdmin)
