from django.contrib import admin

from .models import ChatRoom, Message


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "get_users_count")
    list_filter = ("created_at",)
    search_fields = ("name", "users__email")
    ordering = ("-created_at",)
    filter_horizontal = ("users",)

    def get_users_count(self, obj):
        return obj.users.count()

    get_users_count.short_description = "참가자 수"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("get_short_content", "user", "room", "timestamp")
    list_filter = ("room", "timestamp", "user")
    search_fields = ("content", "user__email", "room__name")
    ordering = ("-timestamp",)
    raw_id_fields = ("user", "room")

    def get_short_content(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    get_short_content.short_description = "메시지 내용"
