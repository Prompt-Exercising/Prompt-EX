from django.http import JsonResponse

from .models import Message


def get_messages(request, room_name):
    messages = Message.objects.filter(room=room_name).order_by("-timestamp")[:50]
    return JsonResponse(
        {"messages": list(messages.values("user__username", "content", "timestamp"))}
    )
