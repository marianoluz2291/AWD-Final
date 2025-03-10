import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from .models import LiveChat

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extract the room_chat name from the URL route parameters
        self.room_chat = self.scope['url_route']['kwargs']['room_chat']
        self.room_chat_name = f'chat_{self.room_chat}'
        await self.channel_layer.group_add(self.room_chat_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Add the WebSocket channel to the chat room group
        await self.channel_layer.group_discard(self.room_chat_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message', None)
        username = text_data_json.get('username', None)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_chat_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
            }
        )

    async def chat_message(self, event):
        # get message and username from the event
        message = event['message']
        username = event['username']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
        }))

    @staticmethod
    async def save_message(sender, receiver, message):
        LiveChat.objects.create(sender=sender, receiver=receiver, message=message)

    @staticmethod
    async def get_user_by_username(username):
        return User.objects.get(username=username)
