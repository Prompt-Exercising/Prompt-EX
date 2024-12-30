import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        from .models import ChatRoom

        # WebSocket URL에서 room_name을 가져옴
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # ChatRoom을 가져오거나 생성
        await self.get_or_create_room(self.room_name)
        # 그룹에 채널 추가
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        # WebSocket 연결 수락
        await self.accept()

    @sync_to_async
    def get_or_create_room(self, room_name):
        from .models import ChatRoom  # 지연 임포트
        ChatRoom.objects.get_or_create(name=room_name)
    
    @sync_to_async
    def save_message(self, room_name, user, content):
        from .models import ChatRoom, Message  # 지연 임포트
        room = ChatRoom.objects.get(name=room_name)
        User = get_user_model()
        user_instance = User.objects.get(email=user.email)
        Message.objects.create(user=user_instance, room=room, content=content)

    async def disconnect(self, close_code):
        # 그룹에서 채널 제거
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json.get("message", "")

        # 메시지를 데이터베이스에 저장
        await self.save_message(self.room_name, self.scope["user"], message_content)

        # 그룹에 메시지 브로드캐스트
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message_content,
                "user": self.scope["user"].username,
            },
        )

    async def chat_message(self, event):
        # 그룹에서 브로드캐스트된 메시지를 WebSocket으로 전송
        await self.send(
            text_data=json.dumps(
                {
                    "message": event["message"],
                    "user": event["user"],
                }
            )
        )

