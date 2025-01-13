import json
import jwt
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from django.contrib.auth import get_user_model

class BaseConsumer(AsyncWebsocketConsumer):
    @sync_to_async
    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    async def authenticate(self):
        token = self.scope["query_string"].decode().split("=")[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = payload["user_id"]
            self.scope["user"] = await self.get_user(user_id)
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            await self.close()
            return False

        if self.scope["user"].is_anonymous:
            await self.close()
            return False

        return True

class ChatConsumer(BaseConsumer):
    async def connect(self):
        if not await self.authenticate():
            return

        # room_id를 사용하여 채팅방 ID를 가져옵니다.
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_id = f"chat_{self.room_id}"

        # room_id를 사용하여 채팅방을 가져옵니다.
        chat_room = await self.get_room_by_id(self.room_id)
        if chat_room is None:
            await self.close()
            return

        await self.add_user_to_room(chat_room, self.scope["user"])
        await self.channel_layer.group_add(self.room_group_id, self.channel_name)
        await self.accept()
    
    @sync_to_async
    def get_room_by_id(self, room_id):
        from .models import ChatRoom
        # room_id를 사용하여 채팅방을 가져옵니다.
        try:
            return ChatRoom.objects.get(id=room_id)
        except ChatRoom.DoesNotExist:
            return None

    @sync_to_async
    def add_user_to_room(self, room, user):
        if room and user:
            room.users.add(user)

    @sync_to_async
    def get_or_create_room(self, room_id):
        from .models import ChatRoom
        room, created = ChatRoom.objects.get_or_create(id=room_id)
        return room

    @sync_to_async
    def save_message(self, room_id, user, content):
        from .models import ChatRoom, Message
        room = ChatRoom.objects.get(id=room_id)
        Message.objects.create(user=user, room=room, content=content)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_id, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json.get("message", "")
        if message_content:
            await self.save_message(self.room_id, self.scope["user"], message_content)
            await self.channel_layer.group_send(
                self.room_group_id,
                {
                    "type": "chat_message",
                    "message": message_content,
                    "user": self.scope["user"].email,
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "chat_message",
            "message": event["message"],
            "user": event["user"],
        }))

class ChatListConsumer(BaseConsumer):
    async def connect(self):
        if not await self.authenticate():
            return

        await self.accept()

    @sync_to_async
    def get_user_chat_rooms(self, user):
        return list(user.chat_rooms.values("id", "name", "created_at"))

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if text_data_json.get("type") == "get_chat_rooms":
            chat_rooms = await self.get_user_chat_rooms(self.scope["user"])
            await self.send(text_data=json.dumps({
                "type": "chat_rooms",
                "data": chat_rooms
            }))

    async def disconnect(self, close_code):
        pass
