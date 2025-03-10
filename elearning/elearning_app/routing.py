# routing.py
from django.urls import re_path, path
from .chat import ChatConsumer

# the route to a chatroom which is identified by roomchat using websocket connections
websocket_urlpatterns = [
    path('ws/chat/<str:room_chat>/', ChatConsumer.as_asgi()),
]