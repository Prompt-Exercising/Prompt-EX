from django.db import models

from common.models import CommonModel
from users.models import User


class ChatRoom(CommonModel):
    users = models.ManyToManyField(User, related_name="chat_rooms")
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Message(CommonModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(
        ChatRoom, on_delete=models.CASCADE, related_name="messages"
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} in {self.room.name}: {self.content[:20]}"
