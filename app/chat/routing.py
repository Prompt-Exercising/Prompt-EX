from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("ws/chat/<int:room_id>/", consumers.ChatConsumer.as_asgi()),
    path("ws/chatroom/list/", consumers.ChatListConsumer.as_asgi()),
]
