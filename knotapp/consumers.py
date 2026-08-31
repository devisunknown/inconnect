import hashlib
import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import Chat, Message, UserPresence

SILLY_EMOJIS = ['🤪', '😜', '🥸', '😝', '🤡', '🙃', '😎', '🤓', '🫠', '🤑', '🥴', '😵‍💫', '🫣', '😬', '🧐']

PRESENCE_GROUP = 'presence'


def user_emoji(username):
    idx = int(hashlib.md5(username.encode()).hexdigest(), 16) % len(SILLY_EMOJIS)
    return SILLY_EMOJIS[idx]


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.chat_group_name = f'chat_{self.chat_id}'
        self.username = self.scope['user'].username

        if not self.scope['user'].is_authenticated:
            await self.close()
            return

        await self.channel_layer.group_add(self.chat_group_name, self.channel_name)
        await self.accept()

        await self.send(text_data=json.dumps({
            'type': 'connected',
            'username': self.username,
            'emoji': user_emoji(self.username),
        }))

        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                'type': 'user_joined',
                'username': self.username,
                'emoji': user_emoji(self.username),
            }
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                'type': 'user_left',
                'username': self.username,
            }
        )
        await self.channel_layer.group_discard(self.chat_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get('type', 'message')
        user = self.scope['user']

        if msg_type == 'message':
            content = data.get('message', '').strip()
            if not content:
                return
            message = await self.save_message(user, content)
            if message is None:
                return
            await self.channel_layer.group_send(
                self.chat_group_name,
                {
                    'type': 'chat_message',
                    'message': content,
                    'sender': user.username,
                    'read': message.is_read,
                    'message_id': message.id,
                }
            )
        elif msg_type == 'typing_start':
            await self.channel_layer.group_send(
                self.chat_group_name,
                {
                    'type': 'typing_start',
                    'username': user.username,
                }
            )
        elif msg_type == 'typing_stop':
            await self.channel_layer.group_send(
                self.chat_group_name,
                {
                    'type': 'typing_stop',
                    'username': user.username,
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'sender': event['sender'],
            'read': event.get('read', False),
            'message_id': event.get('message_id'),
        }))

    async def user_joined(self, event):
        if event['username'] == self.username:
            return
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'username': event['username'],
            'emoji': event['emoji'],
        }))

    async def user_left(self, event):
        if event['username'] == self.username:
            return
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'username': event['username'],
        }))

    async def typing_start(self, event):
        if event['username'] == self.username:
            return
        await self.send(text_data=json.dumps({
            'type': 'typing_start',
            'username': event['username'],
        }))

    async def typing_stop(self, event):
        if event['username'] == self.username:
            return
        await self.send(text_data=json.dumps({
            'type': 'typing_stop',
            'username': event['username'],
        }))

    @database_sync_to_async
    def save_message(self, user, content):
        try:
            chat = Chat.objects.get(id=self.chat_id, participants=user)
            return Message.objects.create(chat=chat, sender=user, content=content)
        except Chat.DoesNotExist:
            return None


class PresenceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        if not user.is_authenticated:
            await self.close()
            return
        self.username = user.username
        await self.channel_layer.group_add(PRESENCE_GROUP, self.channel_name)
        await self.set_presence(True)
        await self.accept()
        await self.send(text_data=json.dumps({'type': 'presence_update', 'username': self.username, 'online': True}))
        await self.channel_layer.group_send(
            PRESENCE_GROUP,
            {'type': 'presence_update', 'username': self.username, 'online': True},
        )

    async def disconnect(self, close_code):
        await self.set_presence(False)
        await self.channel_layer.group_send(
            PRESENCE_GROUP,
            {'type': 'presence_update', 'username': self.username, 'online': False},
        )
        await self.channel_layer.group_discard(PRESENCE_GROUP, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('type') == 'ping':
            await self.send(text_data=json.dumps({'type': 'pong'}))

    async def presence_update(self, event):
        if event.get('username') == self.username:
            return
        await self.send(text_data=json.dumps({
            'type': 'presence_update',
            'username': event['username'],
            'online': event['online'],
        }))

    @database_sync_to_async
    def set_presence(self, online):
        presence, _ = UserPresence.objects.get_or_create(user=self.scope['user'])
        presence.is_online = online
        presence.save()
